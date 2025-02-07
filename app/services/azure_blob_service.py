import os
import uuid
from datetime import datetime, timedelta, UTC
from functools import lru_cache

from PIL.ImageFile import ImageFile
from azure.storage.blob import generate_blob_sas, BlobSasPermissions
from azure.storage.blob.aio import BlobServiceClient, ContainerClient
from fastapi import UploadFile, HTTPException

BASE_PATH_IMAGES = "images/"


async def create_file_name(file: UploadFile) -> str:
    current_date = datetime.now().strftime("%Y%m%d_%H%M%S")
    blob_name = f"{current_date}-{uuid.uuid4()}-{file.filename}"
    return blob_name

async def add_base_path_to_file_name(file_name: str) -> str:
    return f"{BASE_PATH_IMAGES}{file_name}"


class AzureBlobService:
    def __init__(self,
                 account_name: str,
                 account_key: str,
                 container_name: str,
    ):

        self.account_name = account_name
        self.account_key = account_key
        # Azure Blob storage client initialization
        try:
            self.container_name = container_name

            self.connection_string = (
                f"DefaultEndpointsProtocol=https;AccountName={account_name};"
                f"AccountKey={account_key};EndpointSuffix=core.windows.net"
            )

            self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

            self.container_client: ContainerClient = self.blob_service_client.get_container_client(self.container_name)

        except Exception as ex:
            raise Exception(f"Error initializing AzureBlobService: {ex}")

    async def ensure_container_exists(self):
        try:
            if not await self.container_client.exists():
                await self.container_client.create_container()
        except Exception as ex:
            raise HTTPException(status_code=500, detail=f"Failed to ensure container existence: {ex}")


    async def upload_image(self, file: bytes, file_name : str):
        try:
            await self.ensure_container_exists()

            file_name = await add_base_path_to_file_name(file_name)

            await self.container_client.upload_blob(name=file_name, data=file, overwrite=False)

        except Exception as ex:
            raise HTTPException(status_code=500, detail=f"File upload failed: {ex}")

    # Download a file from the Azure Blob Storage
    async def download_file(self, blob_name: str) -> bytes:
        try:
            await self.ensure_container_exists()

            blob_client = self.container_client.get_blob_client(blob_name)
            stream = await blob_client.download_blob()
            data = await stream.readall()

            return data
        except Exception as ex:
            raise HTTPException(status_code=404, detail=f"Blob '{blob_name}' not found: {ex}")

    async def generate_sas_token(self, blob_name: str, expiry_hours: int = 1) -> str:
        sas_token = generate_blob_sas(
            account_name=self.account_name,
            container_name=self.container_name,
            blob_name=blob_name,
            account_key=self.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.now(UTC) + timedelta(hours=expiry_hours)
        )
        return f"https://{self.account_name}.blob.core.windows.net/{self.container_name}/{blob_name}?{sas_token}"


@lru_cache()
def get_azure_blob_service():
    return AzureBlobService(
        account_name=os.getenv('AZURE_STORAGE_ACCOUNT_NAME'),
        account_key=os.getenv('AZURE_STORAGE_ACCOUNT_KEY'),
        container_name=os.getenv('AZURE_STORAGE_CONTAINER_NAME')
    )
