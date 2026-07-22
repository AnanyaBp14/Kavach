from minio import Minio
from src.config.settings import settings
import structlog
from typing import Any
from datetime import timedelta

logger = structlog.get_logger()

class MinioStorageService:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        self.bucket = settings.MINIO_BUCKET_NAME
        self._ensure_bucket()

    def _ensure_bucket(self):
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
                logger.info("Created MinIO bucket", bucket=self.bucket)
        except Exception as e:
            logger.error("Failed to ensure MinIO bucket", error=str(e))

    def upload_file(self, object_key: str, data: Any, length: int, content_type: str) -> str:
        self.client.put_object(
            self.bucket,
            object_key,
            data,
            length=length,
            content_type=content_type
        )
        return f"{settings.MINIO_ENDPOINT}/{self.bucket}/{object_key}"
        
    def get_presigned_url(self, object_key: str, expires_in_minutes: int = 60) -> str:
        return self.client.presigned_get_object(
            self.bucket, 
            object_key, 
            expires=timedelta(minutes=expires_in_minutes)
        )

storage_service = MinioStorageService()
