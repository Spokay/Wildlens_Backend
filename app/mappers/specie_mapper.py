from app.dto.species import SpeciePredictionResponse, SpeciePrediction, FamilyResponse, HabitatResponse, SpecieResponse
from app.models import Specie, Habitat, Family


def habitat_to_response(habitat : Habitat) -> HabitatResponse:
    return HabitatResponse(
        id=habitat.id,
        name=habitat.name,
        description=habitat.description
    )

def family_to_response(family : Family) -> FamilyResponse:
    return FamilyResponse(
        id=family.id,
        name=family.name
    )

def specie_to_response(specie : Specie) -> SpecieResponse:
    family_response = family_to_response(specie.family)
    habitats_response = [habitat_to_response(habitat) for habitat in specie.habitats]

    return SpecieResponse(
        id=specie.id,
        name=specie.name,
        latin_name=specie.latin_name,
        description=specie.description,
        size=specie.size,
        region=specie.region,
        fun_fact=specie.fun_fact,
        family=family_response,
        habitats=habitats_response
    )

def species_to_responses(species: list[Specie]) -> list[SpecieResponse]:
    return [specie_to_response(specie) for specie in species]

def specie_to_prediction_response(specie : Specie, probability: float) -> SpeciePredictionResponse:
    family_response = family_to_response(specie.family)
    habitats_response = [habitat_to_response(habitat) for habitat in specie.habitats]

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
        probability=probability
    )


def species_to_prediction_responses(species: list[Specie], predictions: list[SpeciePrediction]) -> list[SpeciePredictionResponse]:
    return [
        specie_to_prediction_response(specie, prediction.probability) for specie, prediction in zip(species, predictions)
    ]