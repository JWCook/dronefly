"""Module to search iNat site."""

from .api import WWW_BASE_URL
from .places import Place
from .projects import Project
from .taxa import format_taxon_name, get_taxon_fields
from .users import User


def get_place(result):
    """Get place result."""
    place = Place.from_dict(result.get("record"))
    return f":round_pushpin: [{place.display_name}]({place.url})"


def get_project(result):
    """Get project result."""
    project = Project.from_dict(result.get("record"))
    return (
        f":briefcase: [{project.title}]({WWW_BASE_URL}/projects/{project.project_id})"
    )


def get_user(result):
    """Get user result."""
    user = User.from_dict(result.get("record"))
    return f":bust_in_silhouette: {user.profile_link()}"


def get_taxon(result):
    """Get taxon result (v1/search)."""
    taxon = get_taxon_fields(result.get("record"))
    return (
        f":green_circle: [{format_taxon_name(taxon, with_term=True)}]"
        f"({WWW_BASE_URL}/taxa/{taxon.taxon_id})"
    )


def get_taxon2(result):
    """Get taxon result (/v1/taxa)."""
    taxon = get_taxon_fields(result)
    return (
        f":green_circle: [{format_taxon_name(taxon, with_term=True)}]"
        f"({WWW_BASE_URL}/taxa/{taxon.taxon_id})"
    )


# pylint: disable=invalid-name
get_result_type = {
    "Place": get_place,
    "Project": get_project,
    "User": get_user,
    "Taxon": get_taxon,
    "Inactive": get_taxon2,
}


def get_result(result, result_type: str = None):
    """Get fields for any result type."""
    res_type = result_type or result.get("type")
    return get_result_type[res_type](result)


# pylint: disable=too-few-public-methods
class INatSiteSearch:
    """Lookup helper for site search."""

    def __init__(self, cog):
        self.cog = cog

    async def search(self, query, **kwargs):
        """Search iNat site."""

        api_kwargs = {"q": query, "per_page": 30}
        api_kwargs.update(kwargs)
        search_results = await self.cog.api.get_search_results(**api_kwargs)
        result_type = "Inactive" if "is_active" in kwargs else None
        results = [
            get_result(result, result_type) for result in search_results["results"]
        ]
        return (results, search_results["total_results"])
