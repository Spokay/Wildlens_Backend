from typing import Optional

from sqlmodel import Session

from app.dto.users import AuthenticatedUser
from app.models import Specie, Identification


def get_specie_by_class_number(class_number: int, session: Session) -> Specie:
    specie: Optional[Specie] = session.get(Specie, class_number)
    if specie is None:
        raise ValueError(f"Specie with id {class_number} not found")

    return specie


def save_identification(
        session: Session,
        authenticated_user: AuthenticatedUser,
        class_number: int,
        blob_key: str
) -> Identification:
    identification = Identification(
        user_id=authenticated_user.user_id,
        specie_id=class_number,
        file_storage_key=blob_key
    )
    session.add(identification)
    session.commit()
    session.refresh(identification)

    # TODO: Check if a badge should be awarded to the user here


    return identification
