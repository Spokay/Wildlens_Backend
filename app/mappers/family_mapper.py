from functools import lru_cache

from app.dto.family import FamilyResponse
from app.models import Family


class FamilyMapper:

    async def family_to_response(self, family: Family) -> FamilyResponse:
        return FamilyResponse(
            id=family.id,
            name=family.name
        )


@lru_cache()
def get_family_mapper():
    return FamilyMapper()