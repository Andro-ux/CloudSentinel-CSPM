def normalize_instance(instance):
    return {
        "cloud": "gcp",
        "service": "Compute",
        "resource_type": "VM",

        "resource_id": instance["id"],

        "name": instance["name"],

        "zone": instance["zone"],

        "machine_type": instance["machine_type"],

        "status": instance["status"],

        "has_public_ip": any(
            nic.get("accessConfigs")
            for nic in instance["network_interfaces"]
        ),

        "service_accounts": [
            sa["email"]
            for sa in instance["service_accounts"]
        ],

        "raw": instance
    }