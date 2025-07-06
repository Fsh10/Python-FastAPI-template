from fastapi import UploadFile

from src.constants import get_random_guid

from .connection import S3_CLIENT, S3_CLIENT_STATIC_BACKEND


class FileManager(object):
    @staticmethod
    async def upload_file(
        file: UploadFile, old_file_link: str | None = None, folder: str | None = None
    ) -> str:
        """Upload file to S3 storage."""
        unique_file_id = get_random_guid()

        if not old_file_link:
            return await S3_CLIENT.upload_file(
                file=file, name=unique_file_id, folder=folder
            )

        await FileManager.delete_file(file_name=old_file_link.split("/", 4)[-1])
        return await S3_CLIENT.upload_file(
            file=file, name=unique_file_id, folder=folder
        )

    @staticmethod
    async def delete_file(file_name: str):
        """Delete file from S3 storage."""
        await S3_CLIENT.delete_file(object_name=file_name)

    @staticmethod
    async def upload_static_backend_file(
        file: UploadFile, old_file_link: str | None = None, folder: str | None = None
    ) -> str:
        """Upload file to static_backend folder in S3."""
        unique_file_id = get_random_guid()

        if not old_file_link:
            return await S3_CLIENT_STATIC_BACKEND.upload_file(
                file=file,
                name=unique_file_id,
                folder=f"static_backend/{folder}" if folder else "static_backend",
            )

        await FileManager.delete_static_backend_file(
            file_name=old_file_link.split("/", 4)[-1]
        )
        return await S3_CLIENT_STATIC_BACKEND.upload_file(
            file=file,
            name=unique_file_id,
            folder=f"static_backend/{folder}" if folder else "static_backend",
        )

    @staticmethod
    async def delete_static_backend_file(file_name: str):
        """Delete file from static_backend folder in S3."""
        await S3_CLIENT_STATIC_BACKEND.delete_file(object_name=file_name)

    @staticmethod
    async def download_static_backend_file(file_name: str) -> bytes:
        """Download file from static_backend folder in S3."""
        return await S3_CLIENT_STATIC_BACKEND.download_file(object_name=file_name)

    @staticmethod
    async def list_static_backend_files(prefix: str = "") -> list:
        """Get list of files from static_backend folder in S3."""
        return await S3_CLIENT_STATIC_BACKEND.get_all_file_ids(
            prefix=f"static_backend/{prefix}"
        )

    @staticmethod
    def get_static_backend_file_link(file_name: str) -> str:
        """Get file link from static_backend folder."""
        return S3_CLIENT_STATIC_BACKEND.get_file_link(f"static_backend/{file_name}")

    @staticmethod
    async def get_static_backend_presigned_url(
        file_name: str, expiration: int = 3600
    ) -> str:
        """Get presigned URL for file in static_backend folder."""
        return await S3_CLIENT_STATIC_BACKEND.generate_presigned_url(
            f"static_backend/{file_name}", expiration
        )

    @staticmethod
    def extract_file_key_from_url(url: str) -> str:
        """Extract file key from URL."""
        if "/" in url:
            return url.split("/", 4)[-1]
        return url

    @staticmethod
    async def get_presigned_url_from_stored_link(
        stored_link: str, expiration: int = 3600
    ) -> str:
        """Get presigned URL from stored link."""
        if not stored_link:
            return ""

        file_key = FileManager.extract_file_key_from_url(stored_link)

        return await S3_CLIENT_STATIC_BACKEND.generate_presigned_url(
            file_key, expiration
        )
