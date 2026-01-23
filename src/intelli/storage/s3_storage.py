"""S3-compatible storage backend using aioboto3."""

from collections.abc import AsyncIterator
from datetime import datetime
from typing import BinaryIO

import aioboto3
from botocore.exceptions import ClientError

from intelli.config import settings
from intelli.core.exceptions import NotFoundError, StorageError
from intelli.storage.base import StorageBackend, StorageMetadata


class S3StorageBackend(StorageBackend):
    """S3-compatible storage backend (works with AWS S3, MinIO, etc.)."""

    def __init__(
        self,
        bucket: str | None = None,
        endpoint_url: str | None = None,
        access_key: str | None = None,
        secret_key: str | None = None,
        region: str | None = None,
    ):
        """Initialize S3 storage backend.

        Args:
            bucket: S3 bucket name (defaults to settings)
            endpoint_url: S3 endpoint URL (for MinIO, etc.)
            access_key: AWS access key
            secret_key: AWS secret key
            region: AWS region
        """
        self.bucket = bucket or settings.s3_bucket
        self.endpoint_url = endpoint_url or settings.s3_endpoint_url
        self.access_key = access_key or settings.s3_access_key
        self.secret_key = secret_key or settings.s3_secret_key
        self.region = region or settings.s3_region

        self._session = aioboto3.Session(
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region,
        )

    def _get_uri(self, key: str) -> str:
        """Get the S3 URI for a key."""
        return f"s3://{self.bucket}/{key}"

    async def put(
        self,
        key: str,
        content: BinaryIO | bytes,
        content_type: str,
        metadata: dict | None = None,
    ) -> str:
        """Store content in S3."""
        try:
            async with self._session.client(
                "s3",
                endpoint_url=self.endpoint_url,
            ) as s3:
                body = content if isinstance(content, bytes) else content.read()
                extra_args = {
                    "ContentType": content_type,
                }
                if metadata:
                    extra_args["Metadata"] = {k: str(v) for k, v in metadata.items()}

                await s3.put_object(
                    Bucket=self.bucket,
                    Key=key,
                    Body=body,
                    **extra_args,
                )
                return self._get_uri(key)
        except ClientError as e:
            raise StorageError(
                message=f"Failed to put object: {e}",
                operation="put",
            ) from e

    async def get(self, key: str) -> AsyncIterator[bytes]:
        """Stream content from S3."""
        try:
            async with self._session.client(
                "s3",
                endpoint_url=self.endpoint_url,
            ) as s3:
                response = await s3.get_object(Bucket=self.bucket, Key=key)
                async with response["Body"] as stream:
                    async for chunk in stream.iter_chunks():
                        yield chunk
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                raise NotFoundError(resource_type="artifact", identifier=key) from e
            raise StorageError(
                message=f"Failed to get object: {e}",
                operation="get",
            ) from e

    async def get_bytes(self, key: str) -> bytes:
        """Get content as bytes from S3."""
        try:
            async with self._session.client(
                "s3",
                endpoint_url=self.endpoint_url,
            ) as s3:
                response = await s3.get_object(Bucket=self.bucket, Key=key)
                return await response["Body"].read()
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                raise NotFoundError(resource_type="artifact", identifier=key) from e
            raise StorageError(
                message=f"Failed to get object: {e}",
                operation="get_bytes",
            ) from e

    async def get_metadata(self, key: str) -> StorageMetadata | None:
        """Get object metadata from S3."""
        try:
            async with self._session.client(
                "s3",
                endpoint_url=self.endpoint_url,
            ) as s3:
                response = await s3.head_object(Bucket=self.bucket, Key=key)
                return StorageMetadata(
                    content_type=response.get("ContentType", "application/octet-stream"),
                    content_length=response.get("ContentLength", 0),
                    etag=response.get("ETag"),
                    last_modified=response.get("LastModified"),
                )
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return None
            raise StorageError(
                message=f"Failed to get metadata: {e}",
                operation="get_metadata",
            ) from e

    async def exists(self, key: str) -> bool:
        """Check if object exists in S3."""
        try:
            async with self._session.client(
                "s3",
                endpoint_url=self.endpoint_url,
            ) as s3:
                await s3.head_object(Bucket=self.bucket, Key=key)
                return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            raise StorageError(
                message=f"Failed to check existence: {e}",
                operation="exists",
            ) from e

    async def delete(self, key: str) -> bool:
        """Delete object from S3."""
        try:
            # Check if exists first
            exists = await self.exists(key)
            if not exists:
                return False

            async with self._session.client(
                "s3",
                endpoint_url=self.endpoint_url,
            ) as s3:
                await s3.delete_object(Bucket=self.bucket, Key=key)
                return True
        except ClientError as e:
            raise StorageError(
                message=f"Failed to delete object: {e}",
                operation="delete",
            ) from e

    async def generate_presigned_url(
        self,
        key: str,
        expiration_seconds: int = 3600,
        method: str = "GET",
    ) -> str:
        """Generate pre-signed URL for S3 object."""
        try:
            async with self._session.client(
                "s3",
                endpoint_url=self.endpoint_url,
            ) as s3:
                client_method = "get_object" if method == "GET" else "put_object"
                url = await s3.generate_presigned_url(
                    ClientMethod=client_method,
                    Params={"Bucket": self.bucket, "Key": key},
                    ExpiresIn=expiration_seconds,
                )
                return url
        except ClientError as e:
            raise StorageError(
                message=f"Failed to generate presigned URL: {e}",
                operation="generate_presigned_url",
            ) from e
