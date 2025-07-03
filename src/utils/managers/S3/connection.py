from contextlib import asynccontextmanager

from aiobotocore.session import get_session as get_async_session
from fastapi import UploadFile

from src.config import settings


class S3Client:
    """S3 client for file operations."""
    
    def __init__(
        self,
        access_key: str = settings.S3_ACCESS_KEY_ID,
        secret_key: str = settings.S3_SECRET_ACCESS_KEY,
        endpoint_url: str = settings.S3_ENDPOINT_URL,
        bucket_name: str = settings.S3_BUCKET_NAME,
        region: str = settings.S3_REGION,
    ):
        """Initialize S3 client with configuration."""
        self.config = {
            "aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key,
            "endpoint_url": endpoint_url,
            "region_name": region,
        }
        self.bucket_name = bucket_name
        self.async_session = get_async_session()

    @asynccontextmanager
    async def get_async_client(self):
        """Get async S3 client context manager."""
        async with self.async_session.create_client("s3", **self.config) as client:
            yield client

    async def get_all_file_ids(self, prefix: str = ""):
        """Get list of all files with specified prefix."""
        async with self.get_async_client() as client:
            paginator = client.get_paginator("list_objects_v2")
            async for result in paginator.paginate(Bucket=self.bucket_name):
                ids = []
                if "Contents" in result:
                    for obj in result["Contents"]:
                        if obj["Key"].startswith(prefix):
                            file_name = obj["Key"]
                            ids.append(file_name)
                return ids

    async def upload_file(
        self, file: UploadFile, name: str, folder: str | None = None
    ) -> str:
        """Upload file to S3 bucket."""
        name_without_ext = name.split(".")[0] if "." in name else name
        extension = file.filename.split(".")[-1] if "." in file.filename else ""
        full_file_name = (
            f"{folder}/{name_without_ext}.{extension}"
            if folder
            else f"{name_without_ext}.{extension}"
        )

        file_content = await file.read()

        async with self.get_async_client() as client:
            await client.put_object(
                Bucket=self.bucket_name, Key=full_file_name, Body=file_content
            )
        return self.get_file_link(full_file_name)

    async def download_file(self, object_name: str) -> bytes:
        """Download file from S3 bucket."""
        async with self.get_async_client() as client:
            response = await client.get_object(Bucket=self.bucket_name, Key=object_name)
            return await response["Body"].read()

    async def delete_file(self, object_name: str) -> None:
        """Delete file from S3 bucket."""
        async with self.get_async_client() as client:
            await client.delete_object(Bucket=self.bucket_name, Key=object_name)

    async def update_file(self, old_link: str, new_file: UploadFile) -> str:
        """Update file in S3 bucket by replacing old file with new one."""
        object_name = old_link.split("/")[-1]
        await self.delete_file(object_name)
        return await self.upload_file(new_file, object_name)

    def get_file_link(self, file_name: str) -> str:
        """Get public file link from S3 bucket."""
        return f"{self.config['endpoint_url']}/{self.bucket_name}/{file_name}"

    async def generate_presigned_url(
        self, object_name: str, expiration: int = 3600
    ) -> str:
        """Generate presigned URL for secure file access."""
        async with self.get_async_client() as client:
            try:
                url = await client.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": self.bucket_name, "Key": object_name},
                    ExpiresIn=expiration,
                )
                return url
            except Exception as e:
                return self.get_file_link(object_name)


S3_CLIENT = S3Client()
S3_CLIENT_STATIC_BACKEND = S3Client(bucket_name=settings.S3_BUCKET_NAME)
