from fastapi import Depends
from functools import lru_cache

from app.dto.identification import IdentificationResponse
from app.models import Identification
from app.services.azure_blob_service import get_azure_blob_service


class IdentificationMapper:
    def __init__(self, azure_blob_service=Depends(get_azure_blob_service)):
        self.azure_blob_service = azure_blob_service

    async def identification_to_response(self, identification: Identification) -> IdentificationResponse:

        return IdentificationResponse(
            user_id=identification.user_id,
            specie_id=identification.specie_id,
            file_storage_key=identification.file_storage_key,
            date_identified=identification.date_identified
        )

@lru_cache()
def get_identification_mapper():
    return IdentificationMapper(
        azure_blob_service=get_azure_blob_service(),
    )