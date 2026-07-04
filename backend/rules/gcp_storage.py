import hashlib


def make_id(resource_id, title):
    return hashlib.sha256(f"{resource_id}:{title}".encode()).hexdigest()


def evaluate_bucket(bucket):

    findings = []

    if not bucket["versioning"]:
        findings.append({
            "id": make_id(bucket["resource_id"], "Versioning Disabled"),
            "cloud": "gcp",
            "severity": "MEDIUM",
            "service": "Storage",
            "resource_id": bucket["resource_id"],
            "title": "Bucket Versioning Disabled",
            "description": f"Bucket '{bucket['name']}' does not have object versioning enabled.",
            "recommendation": "Enable object versioning to protect against accidental deletion and ransomware."
        })

    if bucket["public_access_prevention"] != "enforced":
        findings.append({
            "id": make_id(bucket["resource_id"], "Public Access Prevention"),
            "cloud": "gcp",
            "severity": "HIGH",
            "service": "Storage",
            "resource_id": bucket["resource_id"],
            "title": "Public Access Prevention Disabled",
            "description": f"Bucket '{bucket['name']}' allows public access.",
            "recommendation": "Enable Public Access Prevention."
        })

    if not bucket["uniform_bucket_level_access"]:
        findings.append({
            "id": make_id(bucket["resource_id"], "Uniform Access"),
            "cloud": "gcp",
            "severity": "MEDIUM",
            "service": "Storage",
            "resource_id": bucket["resource_id"],
            "title": "Uniform Bucket-Level Access Disabled",
            "description": f"Bucket '{bucket['name']}' is using legacy ACLs.",
            "recommendation": "Enable Uniform Bucket-Level Access."
        })

    return findings