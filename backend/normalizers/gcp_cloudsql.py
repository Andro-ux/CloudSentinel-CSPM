def normalize_sql_instance(instance):

    settings = instance.get("settings", {})

    ip_addresses = instance.get("ipAddresses", [])

    backup = settings.get(
        "backupConfiguration",
        {}
    )

    return {

        "service": "Cloud SQL",

        "resource_type": "SQLInstance",

        "resource_id": instance["name"],

        "name": instance["name"],

        "database_version":
            instance.get("databaseVersion"),

        "state":
            instance.get("state"),

        "region":
            instance.get("region"),

        "public_ip":
            any(
                ip.get("type") == "PRIMARY"
                for ip in ip_addresses
            ),

        "backup_enabled":
            backup.get(
                "enabled",
                False
            ),

        "point_in_time_recovery":
            backup.get(
                "pointInTimeRecoveryEnabled",
                False
            ),

        "deletion_protection":
            settings.get(
                "deletionProtectionEnabled",
                False
            ),

        "availability":
            settings.get(
                "availabilityType"
            ),

        "ssl_mode":
            settings.get(
                "ipConfiguration",
                {}
            ).get(
                "sslMode"
            ),

        "authorized_networks":
            settings.get(
                "ipConfiguration",
                {}
            ).get(
                "authorizedNetworks",
                []
            ),
    }