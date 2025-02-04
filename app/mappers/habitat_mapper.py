from functools import lru_cache

from app.dto.habitat import HabitatResponse
from app.models import Habitat


class HabitatMapper:

    async def habitat_to_response(self, habitat: Habitat) -> HabitatResponse:
        return HabitatResponse(
            id=habitat.id,
            name=habitat.name,
            description=habitat.description
        )


@lru_cache()
def get_habitat_mapper():
    return HabitatMapper()