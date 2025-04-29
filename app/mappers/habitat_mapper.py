from functools import lru_cache

from app.dto.habitat import HabitatResponse
from app.models import Habitat


class HabitatMapper:
    async def habitat_to_response(self, habitat: Habitat) -> HabitatResponse:
        return HabitatResponse(
            id=habitat.id, name=habitat.name, description=habitat.description
        )

    async def habitat_list_to_response(
        self, habitats: list[Habitat]
    ) -> list[HabitatResponse]:
        return [await self.habitat_to_response(habitat) for habitat in habitats]


@lru_cache()
def get_habitat_mapper():
    return HabitatMapper()

