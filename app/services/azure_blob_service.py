import os
import uuid
from datetime import datetime
from functools import lru_cache

from azure.storage.blob.aio import BlobServiceClient, ContainerClient
from fastapi import UploadFile, HTTPException

BASE_PATH_IMAGES = "images/"

class AzureBlobService:
    def __init__(self, account_name: str, account_key: str, container_name: str):

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


    # Upload a file to the Azure Blob Storage
    async def upload_file(self, file: UploadFile):
        try:
            await self.ensure_container_exists()

            current_date = datetime.now().strftime("%Y%m%d_%H%M%S")
            blob_name = f"{BASE_PATH_IMAGES}{current_date}-{uuid.uuid4()}-{file.filename}"

            async with file.file as file_stream:
                await self.container_client.upload_blob(name=blob_name, data=file_stream, overwrite=True)

            return blob_name
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

@lru_cache()
def get_azure_blob_service():
    return AzureBlobService(
        account_name=os.getenv('AZURE_STORAGE_ACCOUNT_NAME'),
        account_key=os.getenv('AZURE_STORAGE_ACCOUNT_KEY'),
        container_name=os.getenv('AZURE_STORAGE_CONTAINER_NAME')
    )