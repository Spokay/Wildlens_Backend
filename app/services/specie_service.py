from sqlmodel import Session, select

from app.dto.species import SpeciePrediction, SpeciePredictionResponse, SpecieInformationResponse
from app.models import Specie


def get_species_responses(species: list[Specie], predictions: list[SpeciePrediction]) -> list[SpeciePredictionResponse]:
    return [
        SpeciePredictionResponse(specie=specie, probability=prediction.probability) for specie, prediction in zip(species, predictions)
    ]

def get_specie_response(species: Specie) -> SpecieInformationResponse:
    return SpecieInformationResponse(specie=species)

def get_specie_by_class_number(class_number: int, session: Session) -> Specie:
    statement = select(Specie).where(Specie.id == class_number)
    specie = session.exec(statement).one_or_none()

    if specie is None:
        raise ValueError(f"Specie with id {class_number} not found")

    return specie