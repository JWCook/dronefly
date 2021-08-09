"""Module for inat command group."""

import asyncio
import json
import pprint
from typing import Optional, Union

import discord
from redbot.core import checks, commands
from redbot.core.utils.menus import DEFAULT_CONTROLS, menu, start_adding_reactions

from inatcog.base_classes import WWW_BASE_URL
from inatcog.converters.base import InheritableBoolConverter
from inatcog.embeds.common import make_embed
from inatcog.embeds.inat import INatEmbed, INatEmbeds
from inatcog.interfaces import MixinMeta


class CommandsInat(INatEmbeds, MixinMeta):
    """Mixin providing inat command group."""

    @commands.group()
    async def inat(self, ctx):
        """Show/change iNat settings.

        See also `[p]help iNat` to list available `iNat` *commands* and other *Help* topics.
        """

    @commands.command(name="autoobs")
    async def topic_autoobs(self, ctx):
        """*Help* for automatic observation previews.

        When `autoobs` is on for the channel/server:

        Just include a link to an observation in your message, and it will be looked up as if you typed `[p]obs <link>`

        Only the first link per message is looked up.

        Server mods and owners can set this up. See:
        `[p]help inat set autoobs server` and
        `[p]help inat set autoobs` (channel).
        """  # noqa: E501

    @commands.command(name="dot_taxon")
    async def topic_dot_taxon(self, ctx):
        """*Help* for the `.taxon.` lookup feature.

        When `dot_taxon` is on for the channel/server:

        • Surround taxon to lookup with `.`
        • Separate from other text with blanks
        • Only one lookup will be performed per message
        • Taxonomy tree is omitted for `by` or `from` lookups
        • Show the setting with `[p]inat show dot_taxon`

        **Examples:**
        ```
        It's .rwbl. for sure.
        ```
        • behaves like  `[p]taxon rwbl`
        ```
        Check out these .lacebugs by me. , please.
        ```
        • behaves like `[p]tab lacebugs by me`

        Server mods and owners can set this up. See:
        `[p]help inat set dot_taxon server` and
        `[p]help inat set dot_taxon` (channel).
        """
        await ctx.send_help()

    @commands.command(name="macros")
    async def topic_macros(self, ctx):
        """*Help* for *query* macros.

        A *query* or *taxon query* may include *macros* which are expanded to other query terms described below.

        See also: `[p]help query`, `[p]help query_taxon`, and `[p]help groups`.

        __**`Macro`**__`  `__`Expands to`__
        **`my`**`      by me`
        **`home`**`    from home`
        **`rg`**`      opt quality_grade=research`
        **`nid`**`     opt quality_grade=needs_id`
        **`oldest`**`  opt order=asc`
        **`      `**`      order_by=observed_on`
        **`newest`**`  opt order=desc`
        **`      `**`      order_by=observed_on`
        **`reverse`**` opt order_by=asc`
        **`faves`**`   opt popular order_by=votes`
        """  # noqa: E501

    @commands.command(name="groups")
    async def topic_groups(self, ctx):
        """*Help* for *query* macros that are *taxonomic groups*.

        See also: `[p]help macros`, and `[p]help query`.

        **`herps`**`       opt taxon_ids=`
        **`       `**`       20978,26036`
        **`lichenish`**`   opt taxon_ids=`
        **`       `**`       152028,791197,54743,152030,`
        **`       `**`       175541,127378,117881,117869`
        **`       `**`       without_taxon_id=352459`
        **`mothsonly`**`   lepidoptera opt`
        **`       `**`       without_taxon_id=47224`
        **`unknown`**`     opt iconic_taxa=unknown`
        **`       `**`       without_taxon_id=`
        **`       `**`       67333,151817,131236`
        **`waspsonly`**`   apocrita opt`
        **`       `**`       without_taxon_id=`
        **`       `**`       47336,630955`
        """  # noqa: E501

    @commands.command(name="query")
    async def topic_query(self, ctx):
        """*Help* for observation *query* terms.

        A *query* may contain *taxon query* terms, *macros*, and other *query* terms described below.

        See also: `[p]help query_taxon` for *taxon query* help and `[p]help macros` for *macro* help.

        Aside from *taxon*, other *query* terms may be:
        - `by <name>` to match the named user; also `by me` or just `my` (a *macro*) to match yourself
        - `from <place>` to match the named place; also `from home` or just `home` (a *macro*) to match observations from your *home place*
        - `in prj <project>` to match the named *project*
        - `with <term> <value>` to matched the *controlled term* with the given *value*
        **Examples:**
        ```
        [p]obs by benarmstrong
        -> most recently added observation by benarmstrong
        [p]obs insecta by benarmstrong
        -> most recent insecta by benarmstrong
        [p]s obs insecta from canada
        -> search for any insecta from Canada
        [p]s obs insecta with life larva
        -> search for insecta with life stage = larva
        ```
        """  # noqa: E501

    @commands.command(name="query_taxon")
    async def topic_query_taxon(self, ctx):
        """*Help* for *taxon query* terms.

        See also: `[p]help query` and `[p]help macros` to specify what is also shown about a taxon.

        A *taxon query* matches a single taxon. It may contain the following:
        - *id#* of the iNat taxon
        - *initial letters* of scientific or common names
        - *double-quotes* around exact words in the name
        - *rank keywords* filter by ranks (`sp`, `family`, etc.)
        - *4-letter AOU codes* for birds
        - *taxon* `in` *an ancestor taxon*
        **Examples:**
        ```
        [p]taxon family bear
           -> Ursidae (Bears)
        [p]taxon prunella
           -> Prunella (self-heals)
        [p]taxon prunella in animals
           -> Prunella (Accentors)
        [p]taxon wtsp
           -> Zonotrichia albicollis (White-throated Sparrow)
        ```
        """  # noqa: E501

    @commands.command(name="glossary")
    async def topic_counts(self, ctx):
        """*Help* with terminology and abbreviations.

        __**Obs.** = observations__
        __**Leaf taxa** = distinct taxa counted__ (per observer, place, etc.)
        - This is the default way that iNaturalist counts taxa. It is explained here: https://www.inaturalist.org/pages/how_inaturalist_counts_taxa
        __**Spp.** = species *or* leaf taxa__ depending on how they are counted on the related website page.
        - In leaderboard commands like `,topobs`, actual species are counted.
        - In commands counting just a single user like `,my`, *Spp* (species) and *Leaf taxa* are shown.
        - But otherwise, when a display has a *#spp* heading, it refers to *leaf taxa* by default.
        """  # noqa: E501

    @commands.command(name="reactions")
    async def topic_reactions(self, ctx):
        """*Help* for taxon reaction buttons.

        Taxon reaction buttons appear on many different displays.  You may use them only if your iNat account is known in the server.
        - :bust_in_silhouette: to count your observations and species
        - :busts_in_silhouette: to write in another user to count
        - :house: to count your home place obs and species
        - :earth_africa: to write in another place to count
        - :regional_indicator_t: to toggle the taxonomy tree

        See `[p]help user set known` if you're already known in a server and want to be known on other servers.  Otherwise, ask a mod to add you.

        See `[p]help user add` if you're a server owner or mod.
        """  # noqa: E501

    @inat.group(name="set")
    @checks.admin_or_permissions(manage_messages=True)
    async def inat_set(self, ctx):
        """Change `iNat` settings (mods)."""

    @inat.command(name="test", hidden=True)
    async def inat_test(self, ctx):
        """Test command."""
        msg = await ctx.send(
            embed=make_embed(title="Test", description="Reactions test.")
        )
        start_adding_reactions(msg, ["\N{THREE BUTTON MOUSE}"])

    @inat_set.command(name="bot_prefixes")
    @checks.admin_or_permissions(manage_messages=True)
    async def set_bot_prefixes(self, ctx, *prefixes):
        """Set server ignored bot prefixes (mods).

        All messages starting with one of these *prefixes* will be ignored by
        [botname].

        - If *prefixes* is empty, current setting is shown.
        - You particularly need to set *bot_prefixes* if your server has more than one bot with `inatcog` loaded, otherwise it's unlikely you need to set this.
        - Set this to all prefixes of other bots separated by spaces to ensure [botname] ignores commands sent to them, especially when *autoobs* is enabled.
        - You don't need to include any prefixes of [botname] itself.
        """  # noqa: E501
        if ctx.author.bot or ctx.guild is None:
            return

        config = self.config.guild(ctx.guild)

        if prefixes:
            await config.bot_prefixes.set(prefixes)
        else:
            prefixes = await config.bot_prefixes()

        await ctx.send(f"Other bot prefixes are: {repr(list(prefixes))}")

    @inat_set.command(name="inactive_role")
    @checks.admin_or_permissions(manage_roles=True)
    @checks.bot_has_permissions(embed_links=True)
    async def set_inactive_role(self, ctx, inactive_role: Optional[discord.Role]):
        """Set server Inactive role."""
        if ctx.author.bot or ctx.guild is None:
            return

        config = self.config.guild(ctx.guild)

        if inactive_role:
            msg = inactive_role.mention
            await config.inactive_role.set(inactive_role.id)
        else:
            find = await config.inactive_role()
            if find:
                inactive_role = next(
                    (role for role in ctx.guild.roles if role.id == find), None
                )
                msg = (
                    inactive_role.mention
                    if inactive_role
                    else f"missing role: <@&{find}>"
                )
            else:
                msg = "not set"
        await ctx.send(embed=make_embed(description=f"Inactive role: {msg}"))

    @inat_set.command(name="active_role")
    @checks.admin_or_permissions(manage_roles=True)
    @checks.bot_has_permissions(embed_links=True)
    async def set_active_role(self, ctx, active_role: Optional[discord.Role]):
        """Set server Active role."""
        if ctx.author.bot or ctx.guild is None:
            return

        config = self.config.guild(ctx.guild)

        if active_role:
            msg = active_role.mention
            await config.active_role.set(active_role.id)
        else:
            find = await config.active_role()
            if find:
                active_role = next(
                    (role for role in ctx.guild.roles if role.id == find), None
                )
                msg = (
                    active_role.mention if active_role else f"missing role: <@&{find}>"
                )
            else:
                msg = "not set"
        await ctx.send(embed=make_embed(description=f"Active role: {msg}"))

    @inat_set.command(name="beta_role")
    @checks.admin_or_permissions(manage_roles=True)
    @checks.bot_has_permissions(embed_links=True)
    async def set_beta_role(self, ctx, beta_role: Optional[discord.Role]):
        """Set server beta role.

        The beta role grants users with the role early access to `inatcog` features that are not yet released for all users.
        """  # noqa: E501
        if ctx.author.bot or ctx.guild is None:
            return

        config = self.config.guild(ctx.guild)

        if beta_role:
            msg = beta_role.mention
            await config.beta_role.set(beta_role.id)
        else:
            find = await config.beta_role()
            if find:
                beta_role = next(
                    (role for role in ctx.guild.roles if role.id == find), None
                )
                msg = beta_role.mention if beta_role else f"missing role: <@&{find}>"
            else:
                msg = "not set"
        await ctx.send(embed=make_embed(description=f"Beta role: {msg}"))

    @inat.group(name="clear")
    @checks.admin_or_permissions(manage_messages=True)
    async def inat_clear(self, ctx):
        """Clear iNat settings (mods)."""

    @inat_clear.command(name="bot_prefixes")
    @checks.admin_or_permissions(manage_messages=True)
    async def clear_bot_prefixes(self, ctx):
        """Clear server ignored bot prefixes (mods)."""
        if ctx.author.bot or ctx.guild is None:
            return

        config = self.config.guild(ctx.guild)
        await config.bot_prefixes.clear()

        await ctx.send("Server ignored bot prefixes cleared.")

    @inat_set.group(name="autoobs", invoke_without_command=True)
    @checks.admin_or_permissions(manage_messages=True)
    async def set_autoobs(self, ctx, state: InheritableBoolConverter):
        """Set channel auto-observation mode (mods).

        A separate subcommand sets this feature for the whole server. See `[p]help set autoobs server` for details.

        To set the mode for the channel:
        ```
        [p]inat set autoobs on
        [p]inat set autoobs off
        [p]inat set autoobs inherit
        ```
        When `inherit` is specified, channel mode inherits from the server setting.
        """  # noqa: E501
        if ctx.author.bot or ctx.guild is None:
            return

        config = self.config.channel(ctx.channel)
        await config.autoobs.set(state)

        if state is None:
            server_state = await self.config.guild(ctx.guild).autoobs()
            value = f"inherited from server ({'on' if server_state else 'off'})"
        else:
            value = "on" if state else "off"
        await ctx.send(f"Channel observation auto-preview is {value}.")
        return

    @set_autoobs.command(name="server")
    @checks.admin_or_permissions(manage_messages=True)
    async def set_autoobs_server(self, ctx, state: bool):
        """Set server auto-observation mode (mods).

        ```
        [p]inat set autoobs server on
        [p]inat set autoobs server off
        ```

        See `[p]help autoobs` for usage of the feature.
        """
        if ctx.author.bot or ctx.guild is None:
            return

        config = self.config.guild(ctx.guild)
        await config.autoobs.set(state)
        await ctx.send(
            f"Server observation auto-preview is {'on' if state else 'off'}."
        )
        return

    @inat_set.group(invoke_without_command=True, name="dot_taxon")
    @checks.admin_or_permissions(manage_messages=True)
    async def set_dot_taxon(self, ctx, state: InheritableBoolConverter):
        """Set channel .taxon. lookup (mods).

        A separate subcommand sets this feature for the whole server. See `[p]help set dot_taxon server` for details.

        To set .taxon. lookup for the channel:
        ```
        [p]inat set dot_taxon on
        [p]inat set dot_taxon off
        [p]inat set dot_taxon inherit
        ```
        When `inherit` is specified, channel mode inherits from the server setting.

        See `[p]help dot_taxon` for usage of the feature.
        """  # noqa: E501
        if ctx.author.bot or ctx.guild is None:
            return

        config = self.config.channel(ctx.channel)
        await config.dot_taxon.set(state)

        if state is None:
            server_state = await self.config.guild(ctx.guild).dot_taxon()
            value = f"inherited from server ({'on' if server_state else 'off'})"
        else:
            value = "on" if state else "off"
        await ctx.send(f"Channel .taxon. lookup is {value}.")
        return

    @set_dot_taxon.command(name="server")
    @checks.admin_or_permissions(manage_messages=True)
    async def dot_taxon_server(self, ctx, state: bool):
        """Set server .taxon. lookup (mods).

        ```
        [p]inat set dot_taxon server on
        [p]inat set dot_taxon server off
        ```

        See `[p]help dot_taxon` for usage of the feature.
        """
        if ctx.author.bot or ctx.guild is None:
            return

        config = self.config.guild(ctx.guild)
        await config.dot_taxon.set(state)
        await ctx.send(f"Server .taxon. lookup is {'on' if state else 'off'}.")
        return

    @inat.group(name="show")
    async def inat_show(self, ctx):
        """Show iNat settings."""

    @inat.command(name="inspect")
    async def inat_inspect(self, ctx, message_id: Optional[Union[int, str]]):
        """Inspect a message and show any iNat embed contents."""
        try:
            if message_id:
                if isinstance(message_id, str):
                    channel_id, message_id = (
                        int(id_num) for id_num in message_id.split("-")
                    )
                    if ctx.guild:
                        channel = ctx.guild.get_channel(channel_id)
                        if not channel:
                            raise LookupError
                else:
                    channel = ctx.channel
                message = await channel.fetch_message(message_id)
            else:
                ref = ctx.message.reference
                if ref:
                    message = ref.cached_message or await ctx.channel.fetch_message(
                        ref.message_id
                    )
                else:
                    ctx.send_help()
        except discord.errors.NotFound:
            await ctx.send(f"Message not found: {message_id}")
            return
        except LookupError:
            await ctx.send(f"Channel not found: {channel_id}")
            return
        except ValueError:
            await ctx.send("Invalid argument")
            return

        if not message.embeds:
            await ctx.send(f"Message has no embed: {message.jump_url}")
            return

        embeds = []
        inat_embed = INatEmbed.from_discord_embed(message.embeds[0])
        embeds.append(inat_embed)
        inat_inspect = (
            f"```py\n{pprint.pformat(inat_embed.inat_content_as_dict())}\n```"
        )
        inat_inspect_embed = make_embed(
            title="iNat object ids", description=inat_inspect
        )

        if inat_embed.description:
            embed_description = f"```md\n{inat_embed.description}\n```"
            description_embed = make_embed(
                title="Markdown formatted content", description=embed_description,
            )
            embeds.append(description_embed)

        embeds.append(inat_inspect_embed)

        embed_dict = inat_embed.to_dict()
        if "description" in embed_dict:
            del embed_dict["description"]
        attributes_inspect = (
            f"```json\n{json.dumps(embed_dict, indent=4, sort_keys=True)}\n```"
        )
        attributes_embed = make_embed(
            title="Embed attributes", description=attributes_inspect
        )
        embeds.append(attributes_embed)

        await menu(ctx, embeds, DEFAULT_CONTROLS)

    @inat_show.command(name="autoobs")
    async def show_autoobs(self, ctx):
        """Show channel & server auto-observation mode.

        See `[p]help autoobs` to learn about the feature."""
        if ctx.author.bot or ctx.guild is None:
            return

        server_config = self.config.guild(ctx.guild)
        server_state = await server_config.autoobs()
        await ctx.send(
            f"Server observation auto-preview is {'on' if server_state else 'off'}."
        )
        channel_config = self.config.channel(ctx.channel)
        channel_state = await channel_config.autoobs()
        if channel_state is None:
            value = f"inherited from server ({'on' if server_state else 'off'})"
        else:
            value = "on" if channel_state else "off"
        await ctx.send(f"Channel observation auto-preview is {value}.")
        return

    @inat_show.command(name="dot_taxon")
    async def show_dot_taxon(self, ctx):
        """Show channel & server .taxon. lookup.

        See `[p]help dot_taxon` to learn about the feature."""
        if ctx.author.bot or ctx.guild is None:
            return

        server_config = self.config.guild(ctx.guild)
        server_state = await server_config.dot_taxon()
        await ctx.send(f"Server .taxon. lookup is {'on' if server_state else 'off'}.")
        channel_config = self.config.channel(ctx.channel)
        channel_state = await channel_config.dot_taxon()
        if channel_state is None:
            value = f"inherited from server ({'on' if server_state else 'off'})"
        else:
            value = "on" if channel_state else "off"
        await ctx.send(f"Channel .taxon. lookup is {value}.")
        return

    @inat_show.command(name="bot_prefixes")
    async def show_bot_prefixes(self, ctx):
        """Show server ignored bot prefixes."""
        if ctx.author.bot or ctx.guild is None:
            return

        config = self.config.guild(ctx.guild)
        prefixes = await config.bot_prefixes()
        await ctx.send(f"Other bot prefixes are: {repr(list(prefixes))}")

    @inat_set.command(name="home")
    @checks.admin_or_permissions(manage_messages=True)
    async def set_home(self, ctx, home: str):
        """Set server default home place (mods)."""
        config = self.config.guild(ctx.guild)
        try:
            place = await self.place_table.get_place(ctx.guild, home, ctx.author)
        except LookupError as err:
            await ctx.send(err)
            return
        await config.home.set(place.place_id)
        await ctx.send(f"iNat server default home set:\n{place.url}")

    @inat_show.command(name="home")
    async def show_home(self, ctx):
        """Show server default home place."""
        config = self.config.guild(ctx.guild)
        home = await config.home()
        await ctx.send("iNat server default home:")
        try:
            place = await self.place_table.get_place(ctx.guild, int(home), ctx.author)
            await ctx.send(place.url)
        except LookupError as err:
            await ctx.send(err)

    @inat_set.command(name="user_project")
    @checks.admin_or_permissions(manage_roles=True)
    async def set_user_project(
        self, ctx, project_id: int, emoji: Union[str, discord.Emoji]
    ):
        """Add a server user project (mods)."""
        config = self.config.guild(ctx.guild)
        user_projects = await config.user_projects()
        project_id_str = str(project_id)
        if project_id_str in user_projects:
            await ctx.send("iNat user project already known.")
            return

        user_projects[project_id_str] = str(emoji)
        await config.user_projects.set(user_projects)
        await ctx.send("iNat user project added.")

    @inat_clear.command(name="user_project")
    @checks.admin_or_permissions(manage_roles=True)
    async def clear_user_project(self, ctx, project_id: int):
        """Clear a server user project (mods)."""
        config = self.config.guild(ctx.guild)
        user_projects = await config.user_projects()
        project_id_str = str(project_id)

        if project_id_str not in user_projects:
            await ctx.send("iNat user project not known.")
            return

        del user_projects[project_id_str]
        await config.user_projects.set(user_projects)
        await ctx.send("iNat user project removed.")

    @inat_show.command(name="user_projects")
    async def show_user_projects(self, ctx):
        """Show server user projects."""
        config = self.config.guild(ctx.guild)
        user_projects = await config.user_projects()
        for project_id in user_projects:
            await ctx.send(
                f"{user_projects[project_id]} {WWW_BASE_URL}/projects/{project_id}"
            )
            await asyncio.sleep(1)
