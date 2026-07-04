import os

from google.oauth2 import service_account
from google.cloud import storage
from google.cloud import logging as cloud_logging
from googleapiclient.discovery import build

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SERVICE_ACCOUNT_FILE = os.path.join(
    BASE_DIR,
    "credentials",
    "cloudsentinel.json"
)

SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=SCOPES
)


def get_storage_client():
    return storage.Client(
        credentials=credentials,
        project=credentials.project_id
    )


def get_logging_client():
    return cloud_logging.Client(
        credentials=credentials,
        project=credentials.project_id
    )


def get_compute_client():
    return build(
        "compute",
        "v1",
        credentials=credentials
    )


def get_resource_manager_client():
    return build(
        "cloudresourcemanager",
        "v3",
        credentials=credentials
    )


def get_iam_client():
    return build(
        "iam",
        "v1",
        credentials=credentials
    )

def get_project_id():
    return credentials.project_id    