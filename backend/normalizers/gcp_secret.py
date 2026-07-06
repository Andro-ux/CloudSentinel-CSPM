def normalize_secret(secret):

    return {

        "service": "Secret Manager",

        "resource_type": "Secret",

        "resource_id": secret["id"],

        "name": secret["name"],

        "replication": secret["replication"],

        "labels": secret["labels"],

        "create_time": secret["create_time"],
    }