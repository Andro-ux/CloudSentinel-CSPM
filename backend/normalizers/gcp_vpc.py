def normalize_vpc(vpc):

    return {

        "cloud": "gcp",

        "service": "Network",

        "resource_type": "VPC",

        "resource_id": vpc["id"],

        "name": vpc["name"],

        "auto_create_subnets": vpc["autoCreateSubnetworks"],

        "raw": vpc,
    }