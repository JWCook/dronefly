"""Module to access eBird API."""
from redbot.core import commands
import discord
import requests

class INatCog(commands.Cog):
    """An iNaturalist commands cog."""
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def inat(self, ctx):
        """Access the iNat platform."""
        pass # pylint: disable=unnecessary-pass

    @inat.command()
    async def taxon(self, ctx, *terms):
        """Show taxon by id or unique code or name."""
        records = await self.taxa_query(*terms) or []

        color = 0x90ee90
        embed = discord.Embed(color=color)

        if records:
            embed.add_field(
                name=records[0]['name'],
                value=records[0]['preferred_common_name'],
                inline=False,
            )

            embed.set_thumbnail(url=records[0]['default_photo']['square_url'])
        else:
            embed.add_field(
                name='Sorry',
                value='Nothing found',
                inline=False,
            )

        await ctx.send(embed=embed)

    async def taxa_query(self, *terms):
        """Query /taxa for taxa matching terms."""
        inaturalist_api = 'https://api.inaturalist.org/v1/'
        results = requests.get(
            inaturalist_api + 'taxa/',
            headers={'Accept': 'application/json'},
            params={'q':' '.join(terms)},
        ).json()['results']
        return results
