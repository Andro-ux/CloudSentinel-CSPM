def normalize_repository(repository):

    return {

        "cloud": "gcp",

        "service": "Artifact Registry",

        "resource_type": "Repository",

        "resource_id": repository.name,

        "name": repository.name.split("/")[-1],

        "location": repository.name.split("/")[3],

        "format": repository.format_.name,

        "description": repository.description,

        "kms_key": repository.kms_key_name,

        "immutable_tags": repository.docker_config.immutable_tags
        if repository.docker_config
        else False,

        "raw": repository,
    }