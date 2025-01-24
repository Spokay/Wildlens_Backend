from typing import Optional

from sqlmodel import Session

from app.dto.species import SpeciePrediction, SpeciePredictionResponse
from app.models import Specie, User, Identification


def get_specie_prediction_response(specie : Specie, probability: float) -> SpeciePredictionResponse:
    specie_info = specie.model_dump()
    specie_info["probability"] = probability
    return SpeciePredictionResponse(**specie_info)


def get_species_prediction_responses(species: list[Specie], predictions: list[SpeciePrediction]) -> list[SpeciePredictionResponse]:
    return [
        get_specie_prediction_response(specie, prediction.probability) for specie, prediction in zip(species, predictions)
    ]

def get_specie_by_class_number(class_number: int, session: Session) -> Specie:
    specie : Optional[Specie] = session.get(Specie, class_number)
    if specie is None:
        raise ValueError(f"Specie with id {class_number} not found")

    return specie

def save_identification(session: Session, authenticated_user : User, class_number: int, blob_key: str) -> Identification:
    identification = Identification(
        user_id=authenticated_user.id,
        specie_id=class_number,
        file_storage_key=blob_key
    )

    session.add(identification)
    session.commit()
    session.refresh(identification)
    return identification