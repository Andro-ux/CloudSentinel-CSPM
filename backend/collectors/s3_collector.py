import logging

from botocore.exceptions import ClientError

from backend.exceptions import CollectorError
from backend.utils.aws import get_boto3_client

logger = logging.getLogger(__name__)


def collect_s3_buckets(client=None):
    client = client or get_boto3_client("s3")

    if not client:
        raise CollectorError("S3", "Unable to create boto3 client.")

    try:
        response = client.list_buckets()
        buckets = response.get("Buckets", [])

        logger.info("Discovered %d S3 buckets.", len(buckets))

        for bucket in buckets:
            bucket_name = bucket["Name"]

            # Public Access Block
            try:
                pab = client.get_public_access_block(Bucket=bucket_name)
                bucket["PublicAccessBlockConfiguration"] = (
                    pab.get("PublicAccessBlockConfiguration", {})
                )

            except ClientError as e:
                logger.warning(
                    "Public Access Block unavailable for bucket '%s': %s",
                    bucket_name,
                    e.response["Error"]["Code"],
                )
                bucket["PublicAccessBlockConfiguration"] = {}

            # Encryption
            try:
                enc = client.get_bucket_encryption(Bucket=bucket_name)
                bucket["ServerSideEncryptionConfiguration"] = (
                    enc.get("ServerSideEncryptionConfiguration", {})
                )

            except ClientError as e:
                logger.warning(
                    "Encryption configuration unavailable for bucket '%s': %s",
                    bucket_name,
                    e.response["Error"]["Code"],
                )
                bucket["ServerSideEncryptionConfiguration"] = {}

            # ACL
            try:
                acl = client.get_bucket_acl(Bucket=bucket_name)
                bucket["Grants"] = acl.get("Grants", [])

            except ClientError as e:
                logger.warning(
                    "ACL unavailable for bucket '%s': %s",
                    bucket_name,
                    e.response["Error"]["Code"],
                )
                bucket["Grants"] = []

        return buckets

    except ClientError as e:
        error_code = e.response["Error"]["Code"]

        logger.error(
            "S3 collection failed with AWS error: %s",
            error_code,
        )

        raise CollectorError(
            "S3",
            f"AWS API returned {error_code}",
        ) from e

    except Exception as e:
        logger.exception("Unexpected S3 collector failure.")

        raise CollectorError(
            "S3",
            str(e),
        ) from e