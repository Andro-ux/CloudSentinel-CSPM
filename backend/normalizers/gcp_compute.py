def normalize_instance(instance):

    zone = instance.get(
        "zone", ""
    ).split("/")[-1]

    machine_type = instance.get(
        "machineType", ""
    ).split("/")[-1]

    network_interfaces = instance.get(
        "networkInterfaces", []
    )

    service_accounts = instance.get(
        "serviceAccounts", []
    )

    disks = instance.get(
        "disks", []
    )

    labels = instance.get(
        "labels", {}
    )

    tags = instance.get(
        "tags", {}
    ).get(
        "items", []
    )

    return {

        # ---------- Identity ----------

        "cloud": "gcp",

        "service": "Compute",

        "resource_type": "VM",

        "resource_id": instance.get("id"),

        "name": instance.get("name"),

        "display_name": instance.get("name"),

        # ---------- Inventory ----------

        "zone": zone,

        "machine_type": machine_type,

        "status": instance.get("status"),

        # ---------- Relationships ----------

        "relationships": {

            "service_accounts": [

                sa.get("email")

                for sa in service_accounts

            ],

            "subnets": [

                nic.get(
                    "subnetwork", ""
                ).split("/")[-1]

                for nic in network_interfaces

            ],

            "networks": [

                nic.get(
                    "network", ""
                ).split("/")[-1]

                for nic in network_interfaces

            ],

            "disks": [

                disk.get(
                    "deviceName"
                )

                for disk in disks

            ],

        },

        # ---------- Security ----------

        "security": {

            "public_ip": any(

                nic.get("accessConfigs")

                for nic in network_interfaces

            ),

            "shielded_vm": bool(

                instance.get(
                    "shieldedInstanceConfig"
                )

            ),

        },

        # ---------- Metadata ----------

        "metadata": {

            "labels": labels,

            "tags": tags,

        },

        "raw": instance,
    }