from functools import lru_cache

from fastapi import Depends

from app.dto.species import SpeciePredictionResponse, SpeciePrediction, SpecieResponse
from app.mappers.family_mapper import get_family_mapper
from app.mappers.habitat_mapper import get_habitat_mapper
from app.models import Specie
from app.services.azure_blob_service import get_azure_blob_service


class SpecieMapper:
    def __init__(
            self,
            azure_blob_service = Depends(get_azure_blob_service),
            family_mapper = Depends(get_family_mapper),
            habitat_mapper = Depends(get_habitat_mapper)
    ):
        self.azure_blob_service = azure_blob_service
        self.family_mapper = family_mapper
        self.habitat_mapper = habitat_mapper


    async def specie_to_response(self, specie: Specie) -> SpecieResponse:
        family_response = await self.family_mapper.family_to_response(specie.family)
        habitats_response = [await self.habitat_mapper.habitat_to_response(habitat) for habitat in specie.habitats]

        specie_exemple_photo : bytes = await self.azure_blob_service.download_file(specie.specie_exemple_photo)
        footprint_example_photo : bytes = await self.azure_blob_service.download_file(specie.footprint_exemple_photo)

        return SpecieResponse(
            id=specie.id,
            name=specie.name,
            latin_name=specie.latin_name,
            description=specie.description,
            size=specie.size,
            region=specie.region,
            fun_fact=specie.fun_fact,
            specie_exemple_photo=specie_exemple_photo,
            footprint_exemple_photo=footprint_example_photo,
            family=family_response,
            habitats=habitats_response
        )

    async def species_to_responses(self, species: list[Specie]) -> list[SpecieResponse]:
        return [await self.specie_to_response(specie) for specie in species]

    async def specie_to_prediction_response(self, specie: Specie, probability: float) -> SpeciePredictionResponse:
        family_response = await self.family_mapper.family_to_response(specie.family)
        habitats_response = [await self.habitat_mapper.habitat_to_response(habitat) for habitat in specie.habitats]

        specie_exemple_photo: bytes = await self.azure_blob_service.download_file(specie.specie_exemple_photo)
        footprint_example_photo: bytes = await self.azure_blob_service.download_file(specie.footprint_exemple_photo)

        return SpeciePredictionResponse(
            id=specie.id,
            name=specie.name,
            latin_name=specie.latin_name,
            description=specie.description,
            size=specie.size,
            region=specie.region,
            fun_fact=specie.fun_fact,
            specie_exemple_photo=specie_exemple_photo,
            footprint_exemple_photo=footprint_example_photo,
            family=family_response,
            habitats=habitats_response,
            probability=probability
        )

    async def species_to_prediction_responses(self, species: list[Specie], predictions: list[SpeciePrediction]) -> list[
        SpeciePredictionResponse]:
        return [
            await self.specie_to_prediction_response(specie, prediction.probability) for specie, prediction in
            zip(species, predictions)
        ]


@lru_cache()
def get_specie_mapper():
    return SpecieMapper(
        azure_blob_service=get_azure_blob_service(),
        family_mapper=get_family_mapper(),
        habitat_mapper=get_habitat_mapper()
    )