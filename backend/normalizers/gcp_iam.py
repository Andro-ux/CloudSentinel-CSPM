def normalize_service_account(sa):
    return {
        "cloud": "gcp",
        "service": "IAM",
        "resource_type": "ServiceAccount",
        "resource_id": sa["uniqueId"],
        "name": sa["displayName"],
        "email": sa["email"],
        "project": sa["projectId"],
        "disabled": sa.get("disabled", False),
        "raw": sa,
    }