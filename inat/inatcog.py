"""A cog for using the iNaturalist platform."""
import asyncio
import re
from abc import ABC
from datetime import timedelta
from functools import partial
from typing import DefaultDict, Tuple

import inflect
from pyinaturalist import iNatClient
from redbot.core import commands, Config
from redbot.core.utils.antispam import AntiSpam
from .commands.inat import CommandsInat
from .commands.last import CommandsLast
from .commands.map import CommandsMap
from .commands.obs import CommandsObs
from .commands.place import CommandsPlace
from .commands.project import CommandsProject
from .commands.search import CommandsSearch
from .commands.taxon import CommandsTaxon
from .commands.user import CommandsUser
from .core.apis.inat import INatAPI
from .obs_query import INatObsQuery
from .places import INatPlaceTable
from .projects import INatProjectTable
from .query import INatQuery
from .listeners import Listeners
from .search import INatSiteSearch
from .taxon_query import INatTaxonQuery
from .users import INatUserTable

_SCHEMA_VERSION = 3
_DEVELOPER_BOT_IDS = [614037008217800707, 620938327293558794]
_INAT_GUILD_ID = 525711945270296587
SPOILER_PAT = re.compile(r"\|\|")
DOUBLE_BAR_LIT = "\\|\\|"


class CompositeMetaClass(type(commands.Cog), type(ABC)):
    """
    See https://github.com/mikeshardmind/SinbadCogs/blob/v3/rolemanagement/core.py
    """


# pylint: disable=too-many-ancestors,too-many-instance-attributes
class INatCog(
    Listeners,
    commands.Cog,
    CommandsInat,
    CommandsLast,
    CommandsMap,
    CommandsObs,
    CommandsPlace,
    CommandsProject,
    CommandsSearch,
    CommandsTaxon,
    CommandsUser,
    name="iNat",
    metaclass=CompositeMetaClass,
):
    """Commands provided by `inatcog`."""

    spam_intervals = [
        # spamming too fast is > 1 reaction a second for 3 seconds
        (timedelta(seconds=3), 5),
        # spamming too long is > 1 reaction every two seconds for 20 seconds
        (timedelta(seconds=20), 10),
        # spamming high volume is > 1 reaction every 4 seconds for 3 minutes
        (timedelta(minutes=3), 45),
    ]

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1607)
        self.api = INatAPI()
        self.p = inflect.engine()  # pylint: disable=invalid-name
        self.obs_query = INatObsQuery(self)
        self.taxon_query = INatTaxonQuery(self)
        self.query = INatQuery(self)
        self.user_table = INatUserTable(self)
        self.place_table = INatPlaceTable(self)
        self.project_table = INatProjectTable(self)
        self.site_search = INatSiteSearch(self)
        self.client = iNatClient(
            default_params={"locale": "en", "preferred_place_id": 1}
        )
        self.user_cache_init = {}
        self.reaction_locks = {}
        self.predicate_locks = {}
        self.member_as: DefaultDict[Tuple[int, int], AntiSpam] = DefaultDict(
            partial(AntiSpam, self.spam_intervals)
        )

        self.config.register_global(home=97394, schema_version=3)  # North America
        self.config.register_guild(
            autoobs=False,
            dot_taxon=False,
            active_role=None,
            bot_prefixes=[],
            inactive_role=None,
            user_projects={},  # deprecated (schema <=2); superseded by event_projects
            event_projects={},
            places={},
            home=97394,  # North America
            projects={},
            project_emojis={},  # deprecated
        )
        self.config.register_channel(autoobs=None, dot_taxon=None)
        self.config.register_user(
            home=None, inat_user_id=None, known_in=[], known_all=False
        )
        self._cleaned_up = False
        self._init_task: asyncio.Task = self.bot.loop.create_task(self.initialize())
        self._ready_event: asyncio.Event = asyncio.Event()

    async def cog_before_invoke(self, ctx: commands.Context):
        await self._ready_event.wait()

    async def initialize(self) -> None:
        """Initialization after bot is ready."""
        await self.bot.wait_until_ready()
        await self._migrate_config(await self.config.schema_version(), _SCHEMA_VERSION)
        self._ready_event.set()

    async def _migrate_config(self, from_version: int, to_version: int) -> None:
        if from_version == to_version:
            return

        if from_version < 2 <= to_version:
            # Initial registrations via the developer's own bot were intended
            # to be for the iNat server only. Prevent leakage to other servers.
            # Any other servers using this feature with schema 1 must now
            # re-register each user, or the user must `[p]user set known
            # true` to be known in other servers.
            if self.bot.user.id in _DEVELOPER_BOT_IDS:
                all_users = await self.config.all_users()
                for (user_id, user_value) in all_users.items():
                    if user_value["inat_user_id"]:
                        await self.config.user_from_id(int(user_id)).known_in.set(
                            [_INAT_GUILD_ID]
                        )
            await self.config.schema_version.set(2)

        if from_version < 3 <= to_version:
            # User projects have been renamed to event projects, have changed
            # from a single string value to dict, are keyed by abbrev instead of
            # project id, and have optional creds and role attributes.
            # - see Issue #161
            all_guilds = await self.config.all_guilds()
            for (guild_id, guild_value) in all_guilds.items():
                user_projects = guild_value["user_projects"]
                if user_projects:
                    await self.config.guild_from_id(int(guild_id)).user_projects.clear()
                    await self.config.guild_from_id(int(guild_id)).event_projects.set(
                        {
                            user_projects[project_id]: {
                                "project_id": project_id,
                                "creds": None,
                                "role": None,
                            }
                            for project_id in user_projects
                        }
                    )
            await self.config.schema_version.set(3)

    def cog_unload(self):
        """Cleanup when the cog unloads."""
        if not self._cleaned_up:
            if self._init_task:
                self._init_task.cancel()
            self.bot.loop.create_task(self.api.session.close())
            self._cleaned_up = True
