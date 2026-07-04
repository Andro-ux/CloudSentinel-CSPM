import csv
import logging
import time

from botocore.exceptions import ClientError
from backend.exceptions import CollectorError

from backend.models.asset import Asset
from backend.normalizers.common.asset_normalizer import create_asset
from backend.utils.aws import get_boto3_client

logger = logging.getLogger(__name__)


def collect_iam_users(client=None):
    client = client or get_boto3_client("iam")

    if not client:
        raise CollectorError("IAM", "Unable to create boto3 client.")

    try:
        paginator = client.get_paginator("list_users")

        users = []

        for page in paginator.paginate():
            users.extend(page["Users"])

        for user in users:
            user["AttachedPolicies"] = []

            try:
                pol_paginator = client.get_paginator(
                    "list_attached_user_policies"
                )

                for pol_page in pol_paginator.paginate(
                    UserName=user["UserName"]
                ):
                    user["AttachedPolicies"].extend(
                        pol_page["AttachedPolicies"]
                    )

                inline = client.list_user_policies(
                    UserName=user["UserName"]
                )

                user["InlinePolicies"] = inline.get(
                    "PolicyNames", []
                )

            except ClientError as e:
                logger.warning(
                    "Unable to fetch policies for %s: %s",
                    user["UserName"],
                    e.response["Error"]["Code"],
                )

        return users

    except ClientError as e:
        logger.error("IAM user collection failed: %s", e.response["Error"]["Code"])
        raise CollectorError("IAM", f"AWS API returned {e.response['Error']['Code']}") from e
    except Exception as e:
        logger.exception("Unexpected IAM user collector failure.")
        raise CollectorError("IAM", str(e)) from e


def collect_iam_roles(client=None):
    client = client or get_boto3_client("iam")

    if not client:
        raise CollectorError("IAM", "Unable to create boto3 client.")

    try:
        paginator = client.get_paginator("list_roles")

        roles = []

        for page in paginator.paginate():
            roles.extend(page["Roles"])

        return roles

    except ClientError as e:
        logger.error("IAM role collection failed: %s", e.response["Error"]["Code"])
        raise CollectorError("IAM", f"AWS API returned {e.response['Error']['Code']}") from e
    except Exception as e:
        logger.exception("Unexpected IAM role collector failure.")
        raise CollectorError("IAM", str(e)) from e


def collect_iam_credential_report(client=None):
    client = client or get_boto3_client("iam")

    if not client:
        raise CollectorError("IAM", "Unable to create boto3 client.")

    try:
        client.generate_credential_report()

        retries = 0

        while retries < 10:

            try:
                response = client.get_credential_report()

                content = response["Content"].decode("utf-8")

                reader = csv.DictReader(content.splitlines())

                return list(reader)

            except client.exceptions.CredentialReportNotPresentException:
                time.sleep(2)

            except client.exceptions.CredentialReportNotReadyException:
                time.sleep(2)

            retries += 1

        return []

    except ClientError as e:
        logger.error("Credential report collection failed: %s", e.response["Error"]["Code"])
        raise CollectorError("IAM", f"AWS API returned {e.response['Error']['Code']}") from e
    except Exception as e:
        logger.exception("Unexpected credential report collector failure.")
        raise CollectorError("IAM", str(e)) from e


# ----------------------------------------------------
# New CSPM Inventory Function
# ----------------------------------------------------

def collect_iam_assets(account_id=None, client=None):
    """
    Returns normalized Asset objects for the inventory engine.
    Existing collectors remain unchanged.
    """

    client = client or get_boto3_client("iam")

    if not client:
        raise CollectorError("IAM", "Unable to create boto3 client.")

    assets = []

    users = collect_iam_users(client)

    for user in users:

        tags = {}

        if "Tags" in user:
            tags = {
                t["Key"]: t["Value"]
                for t in user.get("Tags", [])
            }

        assets.append(
            create_asset(
                account_id=account_id,
                service="IAM",
                resource_type="USER",
                resource_id=user["UserId"],
                name=user["UserName"],
                arn=user.get("Arn"),
                region="global",
                tags=tags,
                configuration=user,
            )
        )

    roles = collect_iam_roles(client)

    for role in roles:

        tags = {}

        if "Tags" in role:
            tags = {
                t["Key"]: t["Value"]
                for t in role.get("Tags", [])
            }

        assets.append(
            create_asset(
                account_id=account_id,
                service="IAM",
                resource_type="ROLE",
                resource_id=role["RoleId"],
                name=role["RoleName"],
                arn=role.get("Arn"),
                region="global",
                tags=tags,
                configuration=role,
            )
        )

    logger.info(f"Collected {len(assets)} IAM assets")

    return assets