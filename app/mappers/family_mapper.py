from functools import lru_cache

from app.dto.family import FamilyResponse
from app.models import Family


class FamilyMapper:
    async def family_to_response(self, family: Family) -> FamilyResponse:
        return FamilyResponse(id=family.id, name=family.name)

    async def families_to_response(
        self, families: list[Family]
    ) -> list[FamilyResponse]:
        if not families:
            return []
        return [await self.family_to_response(family) for family in families]


@lru_cache()
def get_family_mapper():
    return FamilyMapper()

