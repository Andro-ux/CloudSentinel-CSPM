import logging

from botocore.exceptions import ClientError

from backend.exceptions import CollectorError
from backend.utils.aws import get_boto3_client

logger = logging.getLogger(__name__)


def collect_trails(client=None):
    client = client or get_boto3_client("cloudtrail")

    if not client:
        raise CollectorError("CloudTrail", "Unable to create boto3 client.")

    try:
        response = client.describe_trails()
        trails = response.get("trailList", [])

        logger.info("Discovered %d CloudTrail trails.", len(trails))

        for trail in trails:
            try:
                status = client.get_trail_status(Name=trail["TrailARN"])
                trail["Status"] = status
            except ClientError as e:
                logger.warning(
                    "Unable to retrieve status for trail '%s': %s",
                    trail.get("Name", trail.get("TrailARN")),
                    e.response["Error"]["Code"],
                )
                trail["Status"] = {}

        return trails

    except ClientError as e:
        code = e.response["Error"]["Code"]
        logger.error("CloudTrail collection failed: %s", code)
        raise CollectorError("CloudTrail", f"AWS API returned {code}") from e

    except Exception as e:
        logger.exception("Unexpected CloudTrail collector failure.")
        raise CollectorError("CloudTrail", str(e)) from e
