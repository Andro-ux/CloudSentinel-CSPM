def normalize_firewall(rule):

    logging_enabled = False

    if rule["log_config"]:
        logging_enabled = (
            rule["log_config"].get("enable", False)
        )

    return {
        "service": "Firewall",

        "resource_type": "FirewallRule",

        "resource_id": str(rule["id"]),

        "name": rule["name"],

        "network": rule["network"],

        "direction": rule["direction"],

        "priority": rule["priority"],

        "disabled": rule["disabled"],

        "source_ranges": rule["source_ranges"],

        "destination_ranges": rule["destination_ranges"],

        "allowed": rule["allowed"],

        "denied": rule["denied"],

        "logging": logging_enabled,

        "target_tags": rule["target_tags"],

        "target_service_accounts": rule[
            "target_service_accounts"
        ],
    }