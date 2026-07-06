def normalize_service(service):

    return {

        "cloud": "gcp",

        "service": "Cloud Run",

        "resource_type": "Service",

        "resource_id": service.name,

        "name": service.name.split("/")[-1],

        "display_name": (
            f"{service.name.split('/')[-1]} "
            f"({service.location})"
        ),

        "location": service.location,

        "ingress": service.ingress.name,

        "service_account": (
            service.template.service_account
        ),

        "launch_stage": (
            service.launch_stage.name
        ),

        "uri": service.uri,

        "raw": service,
    }