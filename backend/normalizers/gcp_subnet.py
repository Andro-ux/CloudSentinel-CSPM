def normalize_subnet(subnet):

    cidr = subnet.get("cidr") or subnet.get("ip_cidr_range") or ""

    vpc = subnet.get("vpc") or subnet.get("network") or ""

    region = subnet.get("region") or ""

    if not region and vpc:
        region = vpc.split("/")[-1] if "/" in vpc else ""

    pga = subnet.get("private_google_access")

    if pga is None:
        pga = subnet.get("private_ip_google_access", False)

    flow_logs = subnet.get("flow_logs")

    if flow_logs is None:
        flow_logs = subnet.get("enable_flow_logs", False)

    return {

        "cloud": "gcp",

        "service": "Network",

        "resource_type": "Subnet",

        "resource_id": subnet["id"],

        "name": subnet["name"],

        "display_name": subnet["name"],

        "cidr": cidr,

        "ip_cidr_range": cidr,

        "vpc": vpc,

        "region": region,

        "private_google_access": pga,

        "flow_logs": flow_logs,

        "description": subnet.get("description", ""),

        "relationships": {

            "vpcs": [vpc] if vpc else [],

        },

        "raw": subnet,

    }
