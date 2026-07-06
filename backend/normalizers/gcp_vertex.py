def normalize_endpoint(endpoint):

    return {

        "cloud": "gcp",

        "service": "Vertex AI",

        "resource_type": "Endpoint",

        "resource_id": endpoint.name,

        "name": endpoint.display_name,

        "display_name": endpoint.display_name,

        "location": endpoint.name.split("/")[3],

        "description": endpoint.description,

        "network": endpoint.network,

        "kms_key": endpoint.encryption_spec.kms_key_name
        if endpoint.encryption_spec
        else "",

        "raw": endpoint,
    }