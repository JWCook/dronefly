from contextlib import asynccontextmanager
from functools import partial
from typing import Optional, Union

import discord
from dronefly.core.clients.inat import iNatClient as CoreiNatClient
from dronefly.core.commands import Context as DroneflyContext
from pyinaturalist import controllers as pyic
from redbot.core import commands

from .utils import get_dronefly_ctx

def asyncify(self, method):
    async def async_wrapper(*args, **kwargs):
        return await self.loop.run_in_executor(None, partial(method, *args, **kwargs))
    return async_wrapper


class iNatClient(CoreiNatClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.projects.add_users = asyncify(self, self.projects.add_users)
        self.projects.delete_users = asyncify(self, self.projects.delete_users)
        self.projects.from_ids = asyncify(self, self.projects.from_ids)

    @asynccontextmanager
    async def set_ctx_from_user(
        self,
        red_ctx: commands.Context,
        author: Optional[Union[discord.Member, discord.User]] = None,
        dronefly_ctx: Optional[DroneflyContext] = None,
    ):
        """A client with both Red and Dronefly command contexts."""
        self.red_ctx = red_ctx
        self.ctx = dronefly_ctx or await get_dronefly_ctx(
            self.red_ctx, author or red_ctx.author
        )
        yield self
