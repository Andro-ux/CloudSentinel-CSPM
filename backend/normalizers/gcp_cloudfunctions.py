def normalize_function(function):

    service_config = function.get(
        "serviceConfig",
        {}
    )

    return {

        "cloud": "gcp",

        "service": "Cloud Functions",

        "resource_type": "Function",

        "resource_id": function["name"],

        "name": function["name"].split("/")[-1],

        "display_name": (
            f"{function['name'].split('/')[-1]} "
            f"({function['location']})"
        ),

        "location": function["location"],

        "runtime": function.get(
            "buildConfig",
            {}
        ).get("runtime"),

        "service_account": service_config.get(
            "serviceAccountEmail",
            ""
        ),

        "ingress": service_config.get(
            "ingressSettings",
            ""
        ),

        "uri": service_config.get(
            "uri",
            ""
        ),

        "raw": function,
    }