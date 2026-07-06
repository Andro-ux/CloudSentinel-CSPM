import os

from google.oauth2 import service_account
from google.cloud import storage
from google.cloud import logging as cloud_logging
from googleapiclient.discovery import build
from google.cloud import secretmanager
from google.cloud import container_v1
from google.cloud import artifactregistry
from google.cloud import run_v2
from google.cloud import pubsub_v1
from google.cloud import aiplatform_v1
from google.cloud import bigquery
from google.cloud import dataflow_v1beta3
from google.cloud import dataproc_v1
from google.api_core.client_options import ClientOptions

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

def get_sqladmin_client():
    return build(
        "sqladmin",
        "v1beta4",
        credentials=credentials
    )   

def get_secretmanager_client():

    return secretmanager.SecretManagerServiceClient(
        credentials=credentials
    )

def get_container_client():

    return container_v1.ClusterManagerClient(
        credentials=credentials
    )

def get_artifact_registry_client():

    return artifactregistry.ArtifactRegistryClient(
        credentials=credentials
    )
def get_run_client():

    return run_v2.ServicesClient(
        credentials=credentials
    )    
def get_cloudfunctions_client():

    return build(
        "cloudfunctions",
        "v2",
        credentials=credentials
    )    
def get_pubsub_publisher_client():

    return pubsub_v1.PublisherClient(
        credentials=credentials
    )    
def get_vertex_ai_client():

    return aiplatform_v1.EndpointServiceClient(
        credentials=credentials
    )    
def get_bigquery_client():

    return bigquery.Client(
        credentials=credentials,
        project=credentials.project_id
    )
def get_dataflow_client():

    return dataflow_v1beta3.JobsV1Beta3Client(
        credentials=credentials
    )   
def get_dataproc_client(region):

    return dataproc_v1.ClusterControllerClient(

        credentials=credentials,

        client_options=ClientOptions(
            api_endpoint=f"{region}-dataproc.googleapis.com:443"
        ),
    )    


def get_project_id():
    return credentials.project_id    