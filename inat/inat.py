"""A cog for using the iNaturalist platform."""
import asyncio
from datetime import timedelta
from functools import partial
import textwrap
from typing import DefaultDict, Tuple

import discord
import inflect
from pyinaturalist import iNatClient
from redbot.core import commands, Config
from redbot.core.utils.antispam import AntiSpam
from .core.apis.inat import INatAPI
from .core.formatters.constants import WWW_BASE_URL
from .core.formatters.discord import EMBED_COLOR, MAX_EMBED_DESCRIPTION_LEN

_SCHEMA_VERSION = 2
_DEVELOPER_BOT_IDS = [614037008217800707, 620938327293558794]
_INAT_GUILD_ID = 525711945270296587


# pylint: disable=too-many-ancestors,too-many-instance-attributes
class INat(commands.Cog, name="iNat"):
    """Commands provided by `inat`."""

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
        self.client = iNatClient(
            default_params={"locale": "en", "preferred_place_id": 1}
        )
        self.user_cache_init = {}
        self.reaction_locks = {}
        self.predicate_locks = {}
        self.member_as: DefaultDict[Tuple[int, int], AntiSpam] = DefaultDict(
            partial(AntiSpam, self.spam_intervals)
        )

        self.config.register_global(home=97394, schema_version=1)  # North America
        self.config.register_guild(
            autoobs=False,
            dot_taxon=False,
            active_role=None,
            bot_prefixes=[],
            inactive_role=None,
            user_projects={},
            places={},
            home=97394,  # North America
            projects={},
            project_emojis={},
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

    def cog_unload(self):
        """Cleanup when the cog unloads."""
        if not self._cleaned_up:
            if self._init_task:
                self._init_task.cancel()
            self.bot.loop.create_task(self.api.session.close())
            self._cleaned_up = True

    @commands.command()
    async def ttest(self, ctx, *, query: str):
        """Taxon via pyinaturalist (test)."""
        taxa = await ctx.bot.loop.run_in_executor(
            None, partial(self.client.taxa.autocomplete, q=query)
        )
        if taxa:
            taxon = taxa[0]
            embed = discord.Embed(color=EMBED_COLOR)

            # Show enough of the record for a satisfying test.
            embed.title = taxon.name
            embed.url = f"{WWW_BASE_URL}/taxa/{taxon.id}"
            default_photo = taxon.default_photo
            if default_photo:
                medium_url = default_photo.medium_url
                if medium_url:
                    embed.set_image(url=medium_url)
                    embed.set_footer(text=default_photo.attribution)
            embed.description = (
                "```py\n"
                + textwrap.shorten(
                    f"{repr(taxon)}",
                    width=MAX_EMBED_DESCRIPTION_LEN
                    - 10,  # i.e. minus the code block markup
                    placeholder="…",
                )
                + "\n```"
            )
            await ctx.send(embed=embed)
