def normalize_cloud_armor(policy):

    return {

        "service": "Cloud Armor",

        "resource_type": "SecurityPolicy",

        "resource_id": policy["id"],

        "name": policy["name"],

        "description": policy["description"],

        "type": policy["type"],

        "rules": policy["rules"],
    }