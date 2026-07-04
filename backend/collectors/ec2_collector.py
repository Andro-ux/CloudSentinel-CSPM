import logging

from botocore.exceptions import ClientError

from backend.exceptions import CollectorError
from backend.utils.aws import get_boto3_client

logger = logging.getLogger(__name__)


def collect_security_groups(client=None):
    client = client or get_boto3_client("ec2")

    if not client:
        raise CollectorError("EC2", "Unable to create boto3 client.")

    try:
        paginator = client.get_paginator("describe_security_groups")

        security_groups = []

        for page in paginator.paginate():
            security_groups.extend(page["SecurityGroups"])

        logger.info("Discovered %d security groups.", len(security_groups))

        return security_groups

    except ClientError as e:
        error_code = e.response["Error"]["Code"]

        logger.error(
            "EC2 Security Group collection failed: %s",
            error_code,
        )

        raise CollectorError(
            "EC2",
            f"AWS API returned {error_code}",
        ) from e

    except Exception as e:
        logger.exception("Unexpected EC2 collector failure.")

        raise CollectorError(
            "EC2",
            str(e),
        ) from e
