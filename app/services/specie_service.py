import os
import tempfile
import aiofiles
from typing import Optional

from fastapi import HTTPException, UploadFile
from sqlmodel import Session, select
from starlette import status

from app.dto.species import SpecieBasicInfoResponse, UploadInfo
from app.mappers.specie_mapper import SpecieMapper
from app.models import Specie, Identification
from app.services.azure_blob_service import AzureBlobService, create_file_name


async def get_specie_by_class_number(class_number: int, session: Session) -> Specie:
    specie: Optional[Specie] = session.get(Specie, class_number)
    if specie is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Specie with id {class_number} not found"
        )

    return specie

async def save_temporary_file(
        image: UploadFile
) -> (str, str):
    try:
        image.file.seek(0)
        # Create a temporary directory (if needed) and save the file there
        with tempfile.TemporaryDirectory(delete=False) as temp_dir:
            # Generate a unique file name
            image_file_name = await create_file_name(image)
            temp_file_path = os.path.join(temp_dir, image_file_name)

            # Read and save the file
            image_data = await image.read()
            with open(temp_file_path, "wb") as f:
                f.write(image_data)

            # Return the temporary file path (or just the file name, depending on your use case)
            return temp_file_path, image_file_name

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Cannot save the temporary file"
        )


async def upload_blob_from_temp_file(
        upload_info : UploadInfo,
        azure_blob_service : AzureBlobService
):
    try:
        print(upload_info.tmp_file_path)

        async with aiofiles.open(upload_info.tmp_file_path, "rb") as f:
            tmp_img = await f.read()

        await azure_blob_service.upload_image(
            tmp_img,
            upload_info.image_file_name
        )

        if os.path.exists(upload_info.tmp_file_path): os.remove(upload_info.tmp_file_path)


    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Cannot find the temporary file to upload"
        )



async def save_identification(
        session: Session,
        user_id: int,
        specie_id: int,
        blob_name: str
) -> Identification:

    identification = Identification(
        user_id=user_id,
        specie_id=specie_id,
        file_storage_key=blob_name
    )
    session.add(identification)
    session.commit()
    session.refresh(identification)

    return identification


async def get_identified_species_by_user(user_id: int, session: Session, specie_mapper : SpecieMapper) -> list[SpecieBasicInfoResponse]:
    statement = select(Specie).join(Identification).where(Identification.user_id == user_id)

    identified_species = session.exec(statement).all()

    species_response = await specie_mapper.species_to_basic_info_responses(identified_species)

    return species_response