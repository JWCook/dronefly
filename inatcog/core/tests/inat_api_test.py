"""Test INatAPI."""
import json
from unittest.mock import AsyncMock

from aiohttp import ClientSession, web
import pytest

from ..apis.inat import INatAPI


@pytest.fixture(name="inat_api")
async def fixture_inat_api():
    inat_api = INatAPI()
    yield inat_api
    await inat_api.session.close()


@pytest.fixture(name="mock_response")
def fixture_mock_response(mocker):
    async_mock = AsyncMock()
    mocker.patch.object(ClientSession, "get", side_effect=async_mock)
    return async_mock


def web_response(expected_result):
    return web.Response(body=json.dumps(expected_result))


pytestmark = pytest.mark.asyncio


async def test_get_taxa_by_id(inat_api, mock_response):
    """Test get_taxa by id."""
    mock_response.return_value = web_response({"results": [{"name": "Animalia"}]})
    taxon = await inat_api.get_taxa(1)
    assert taxon["results"][0]["name"] == "Animalia"
