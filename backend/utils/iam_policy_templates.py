import os


def get_cloudsentinel_aws_account_id() -> str:
    """The AWS account ID that CloudSentinel runs in. Customers' trust policies
    must grant assume-role access to this account. Must be set in production —
    there is no safe default."""
    account_id = os.getenv("CLOUDSENTINEL_AWS_ACCOUNT_ID")
    if not account_id:
        raise RuntimeError(
            "CLOUDSENTINEL_AWS_ACCOUNT_ID is not set. This must be the AWS account ID "
            "that CloudSentinel's backend runs in, so customer trust policies can be generated."
        )
    return account_id


def build_trust_policy(external_id: str) -> dict:
    """The trust policy a customer attaches to the role they create for CloudSentinel.
    Restricts assumption to CloudSentinel's AWS account AND requires the unique
    external ID, which prevents the confused-deputy problem."""
    cloudsentinel_account_id = get_cloudsentinel_aws_account_id()
    return {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"AWS": f"arn:aws:iam::{cloudsentinel_account_id}:root"},
                "Action": "sts:AssumeRole",
                "Condition": {
                    "StringEquals": {"sts:ExternalId": external_id}
                },
            }
        ],
    }


def build_read_only_policy() -> dict:
    """Least-privilege permissions CloudSentinel needs to run all current rule checks.
    Strictly read-only — no Put/Delete/Create actions anywhere. Update this list any
    time a new collector is added so customers' roles stay in sync with what's scanned."""
    return {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "IAMReadOnly",
                "Effect": "Allow",
                "Action": [
                    "iam:ListUsers",
                    "iam:ListAttachedUserPolicies",
                    "iam:ListUserPolicies",
                    "iam:ListRoles",
                    "iam:GenerateCredentialReport",
                    "iam:GetCredentialReport",
                ],
                "Resource": "*",
            },
            {
                "Sid": "S3ReadOnly",
                "Effect": "Allow",
                "Action": [
                    "s3:ListAllMyBuckets",
                    "s3:GetBucketPublicAccessBlock",
                    "s3:GetEncryptionConfiguration",
                    "s3:GetBucketAcl",
                ],
                "Resource": "*",
            },
            {
                "Sid": "EC2ReadOnly",
                "Effect": "Allow",
                "Action": [
                    "ec2:DescribeSecurityGroups",
                ],
                "Resource": "*",
            },
            {
                "Sid": "CloudTrailReadOnly",
                "Effect": "Allow",
                "Action": [
                    "cloudtrail:DescribeTrails",
                    "cloudtrail:GetTrailStatus",
                ],
                "Resource": "*",
            },
        ],
    }


def build_onboarding_instructions(role_arn_placeholder: str, external_id: str) -> str:
    return (
        "1. In the customer AWS account, create an IAM role (e.g. 'CloudSentinelScanRole').\n"
        "2. Attach the provided read-only policy to the role.\n"
        "3. Set the role's trust policy to the provided trust_policy JSON exactly as given "
        f"(it restricts assumption to CloudSentinel's account AND requires external ID '{external_id}').\n"
        "4. Copy the resulting Role ARN and submit it via POST /accounts (or PATCH if already created with a placeholder).\n"
        "5. Call POST /accounts/{id}/verify to confirm CloudSentinel can assume the role before it's scanned."
    )
