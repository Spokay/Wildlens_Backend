from app.models.response import SpecieResponse
from app.models.specie import Specie, SpeciePrediction


def get_species_responses(species: list[Specie], predictions: list[SpeciePrediction]) -> list[SpecieResponse]:
    return [
        SpecieResponse(specie=specie, probability=prediction.probability) for specie, prediction in zip(species, predictions)
    ]

def get_specie_by_class_number(class_number: int) -> Specie:
    pass