"""Durable storage for PDFs and FAISS indexes: local folder (or Render disk) or any S3-compatible bucket."""
import os
from pathlib import Path

from app.config import settings


class Storage:
    def __init__(self) -> None:
        self.backend = settings.storage_backend
        self._s3 = None
        if self.backend == "s3":
            import boto3

            self._s3 = boto3.client(
                "s3",
                endpoint_url=settings.s3_endpoint_url or None,
                region_name=settings.s3_region or None,
                aws_access_key_id=settings.s3_access_key_id or None,
                aws_secret_access_key=settings.s3_secret_access_key or None,
            )
        else:
            Path(settings.storage_dir).mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        key = key.replace("\\", "/")
        if ".." in key.split("/"):
            raise ValueError("Invalid storage key")
        return Path(settings.storage_dir) / key

    def put(self, key: str, data: bytes) -> None:
        if self._s3:
            self._s3.put_object(Bucket=settings.s3_bucket, Key=key, Body=data)
            return
        p = self._path(key)
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_suffix(p.suffix + ".tmp")
        tmp.write_bytes(data)
        os.replace(tmp, p)

    def get(self, key: str) -> bytes:
        if self._s3:
            return self._s3.get_object(Bucket=settings.s3_bucket, Key=key)["Body"].read()
        return self._path(key).read_bytes()

    def exists(self, key: str) -> bool:
        if self._s3:
            try:
                self._s3.head_object(Bucket=settings.s3_bucket, Key=key)
                return True
            except Exception:
                return False
        return self._path(key).exists()

    def delete(self, key: str) -> None:
        if self._s3:
            self._s3.delete_object(Bucket=settings.s3_bucket, Key=key)
            return
        p = self._path(key)
        if p.exists():
            p.unlink()


storage = Storage()
