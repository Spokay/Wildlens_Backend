from functools import lru_cache
from typing import Union

from fastapi import Depends

from app.dto.species import (
    SpeciePredictionResponse,
    SpeciePrediction,
    SpecieResponse,
    SpecieBasicInfoResponse, SpecieIdentifiedResponse,
)
from app.mappers.family_mapper import get_family_mapper
from app.mappers.habitat_mapper import get_habitat_mapper
from app.mappers.identification_mapper import get_identification_mapper
from app.models import Specie, Identification
from app.services.azure_blob_service import get_azure_blob_service


class SpecieMapper:
    def __init__(
        self,
        azure_blob_service=Depends(get_azure_blob_service),
        family_mapper=Depends(get_family_mapper),
        habitat_mapper=Depends(get_habitat_mapper),
        identification_mapper=Depends(get_identification_mapper)
    ):
        self.azure_blob_service = azure_blob_service
        self.family_mapper = family_mapper
        self.habitat_mapper = habitat_mapper
        self.identification_mapper = identification_mapper

    async def specie_to_response(self, specie: Specie) -> SpecieResponse:
        family_response = await self.family_mapper.family_to_response(specie.family)
        habitats_response = [
            await self.habitat_mapper.habitat_to_response(habitat)
            for habitat in specie.habitats
        ]

        return SpecieResponse(
            id=specie.id,
            name=specie.name,
            latin_name=specie.latin_name,
            description=specie.description,
            size=specie.size,
            region=specie.region,
            fun_fact=specie.fun_fact,
            specie_exemple_photo_url=specie.specie_exemple_photo,
            footprint_exemple_photo_url=specie.footprint_exemple_photo,
            family=family_response,
            habitats=habitats_response,
        )

    async def specie_to_basic_info_response(
        self, specie: Specie
    ) -> SpecieBasicInfoResponse:
        family_response = await self.family_mapper.family_to_response(specie.family)
        habitats_response = [
            await self.habitat_mapper.habitat_to_response(habitat)
            for habitat in specie.habitats
        ]

        return SpecieBasicInfoResponse(
            id=specie.id,
            name=specie.name,
            latin_name=specie.latin_name,
            region=specie.region,
            family=family_response,
            habitats=habitats_response,
        )

    async def specie_identified_to_info_response(self, specie: Specie, identifications: list[Identification]) -> SpecieIdentifiedResponse:
        family_response = await self.family_mapper.family_to_response(specie.family)
        habitats_response = [await self.habitat_mapper.habitat_to_response(habitat) for habitat in specie.habitats]
        identification_response = [
            await self.identification_mapper.identification_to_response(identification) for identification in identifications
        ]

        return SpecieIdentifiedResponse(
            id=specie.id,
            name=specie.name,
            latin_name=specie.latin_name,
            description=specie.description,
            size=specie.size,
            region=specie.region,
            fun_fact=specie.fun_fact,
            specie_exemple_photo_url=specie.specie_exemple_photo,
            footprint_exemple_photo_url=specie.footprint_exemple_photo,
            family=family_response,
            habitats=habitats_response,
            identifications=identification_response
        )

    async def species_to_basic_info_responses(
        self, species: list[Specie]
    ) -> list[SpecieBasicInfoResponse]:
        if not species:
            return []
        return [await self.specie_to_basic_info_response(specie) for specie in species]

    async def species_to_responses(self, species: list[Specie]) -> list[SpecieResponse]:
        return [await self.specie_to_response(specie) for specie in species]

    async def specie_user_to_info_response(self, specie: Specie, user_identifications:list[Identification], is_identified: bool) -> SpecieIdentifiedResponse:
        family_response = await self.family_mapper.family_to_response(specie.family)
        habitats_response = [await self.habitat_mapper.habitat_to_response(habitat) for habitat in specie.habitats]

        return SpecieIdentifiedResponse(
            id=specie.id,
            name=specie.name,
            latin_name=specie.latin_name,
            description=specie.description,
            size=specie.size,
            region=specie.region,
            fun_fact=specie.fun_fact,
            specie_exemple_photo_url=specie.specie_exemple_photo,
            footprint_exemple_photo_url=specie.footprint_exemple_photo,
            family=family_response,
            habitats=habitats_response,
            identifications=user_identifications,
            is_identified=is_identified
        )

    async def species_user_to_info_responses(
            self, species: list[Specie], user_id
    )-> list[SpecieIdentifiedResponse]:
        if not species:
            return []
        return [await self.specie_user_to_info_response(specie, user_id) for specie in species]


    async def specie_with_user_identifications_to_info_responses(self, species_with_user_identifications: list[dict]) -> list[SpecieIdentifiedResponse]:
        responses = []
        for data in species_with_user_identifications:
            specie = data['specie']
            user_identifications = data['user_identifications']
            is_identified = data['is_identified']

            family_response = await self.family_mapper.family_to_response(specie.family)
            habitats_response = [
                await self.habitat_mapper.habitat_to_response(habitat)
                for habitat in specie.habitats
            ]
            identification_response = [
                await self.identification_mapper.identification_to_response(identification)
                for identification in user_identifications
            ]

            response = SpecieIdentifiedResponse(
                id=specie.id,
                name=specie.name,
                latin_name=specie.latin_name,
                description=specie.description,
                size=specie.size,
                region=specie.region,
                fun_fact=specie.fun_fact,
                specie_exemple_photo_url=specie.specie_exemple_photo,
                footprint_exemple_photo_url=specie.footprint_exemple_photo,
                family=family_response,
                habitats=habitats_response,
                identifications=identification_response,
                is_identified=is_identified
            )
            responses.append(response)

        return responses


    async def specie_to_prediction_response(
        self, specie: Specie, probability: float
    ) -> SpeciePredictionResponse:
        family_response = await self.family_mapper.family_to_response(specie.family)
        habitats_response = [
            await self.habitat_mapper.habitat_to_response(habitat)
            for habitat in specie.habitats
        ]

        return SpeciePredictionResponse(
            id=specie.id,
            name=specie.name,
            latin_name=specie.latin_name,
            description=specie.description,
            size=specie.size,
            region=specie.region,
            fun_fact=specie.fun_fact,
            family=family_response,
            habitats=habitats_response,
            probability=probability,
        )

    async def species_to_prediction_responses(
        self, species: list[Specie], predictions: list[SpeciePrediction]
    ) -> list[SpeciePredictionResponse]:
        return [
            await self.specie_to_prediction_response(specie, prediction.probability)
            for specie, prediction in zip(species, predictions)
        ]




@lru_cache()
def get_specie_mapper():
    return SpecieMapper(
        azure_blob_service=get_azure_blob_service(),
        family_mapper=get_family_mapper(),
        habitat_mapper=get_habitat_mapper(),
        identification_mapper=get_identification_mapper()
    )

