import os
import uuid
import logging
import boto3
from botocore.config import Config
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError

logger = logging.getLogger("cloudsentinel.aws")

RETRY_CONFIG = Config(retries={"max_attempts": 5, "mode": "standard"})


class AssumeRoleError(Exception):
    """Raised when CloudSentinel cannot assume the customer's scanning role."""


def generate_external_id() -> str:
    """Generates a unique external ID to bind to a customer's trust policy.

    The external ID prevents the 'confused deputy' problem: without it, anyone who
    learns a customer's Role ARN could potentially assume it from their own AWS
    account. AWS recommends a unique, hard-to-guess value per third party integration.
    """
    return f"cloudsentinel-{uuid.uuid4()}"


def assume_role(role_arn: str, external_id: str, session_name: str = "cloudsentinel-scan"):
    """Assumes a customer's scanning role via STS and returns temporary credentials.

    Returns a dict of temporary credentials (AccessKeyId, SecretAccessKey, SessionToken,
    Expiration), or raises AssumeRoleError if the assumption fails (bad trust policy,
    wrong external id, role deleted, etc).
    """
    sts_client = boto3.client("sts", config=RETRY_CONFIG)
    try:
        response = sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName=session_name,
            ExternalId=external_id,
            DurationSeconds=3600,
        )
        return response["Credentials"]
    except ClientError as e:
        logger.error(f"Failed to assume role {role_arn}: {e}")
        raise AssumeRoleError(str(e)) from e


def get_boto3_client_for_account(account, service_name: str):
    """Returns a boto3 client scoped to a customer Account via STS AssumeRole.

    `account` is a backend.database.models.Account instance. Raises AssumeRoleError
    if the role cannot be assumed (caller should mark the account/scan as failed,
    not silently treat it as "zero resources").
    """
    creds = assume_role(account.role_arn, account.external_id)
    region = account.region or os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    return boto3.client(
        service_name,
        region_name=region,
        aws_access_key_id=creds["AccessKeyId"],
        aws_secret_access_key=creds["SecretAccessKey"],
        aws_session_token=creds["SessionToken"],
        config=RETRY_CONFIG,
    )


def get_boto3_client(service_name: str, region_name: str = None):
    """
    Returns a boto3 client for the requested service.
    Falls back to standard AWS credentials chain if explicit env keys are not provided.
    """
    region = region_name or os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    
    # Configure robust retry config with standard retry mode and 5 max attempts
    config = Config(
        retries={
            'max_attempts': 5,
            'mode': 'standard'
        }
    )
    
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_session_token = os.getenv("AWS_SESSION_TOKEN")
    
    kwargs = {
        "region_name": region,
        "config": config
    }
    
    if aws_access_key and aws_secret_key:
        kwargs["aws_access_key_id"] = aws_access_key
        kwargs["aws_secret_access_key"] = aws_secret_key
        if aws_session_token:
            kwargs["aws_session_token"] = aws_session_token
            
    try:
        client = boto3.client(service_name, **kwargs)
        return client
    except (NoCredentialsError, PartialCredentialsError) as e:
        print(f"AWS Credentials Error for {service_name}: {e}")
        return None

