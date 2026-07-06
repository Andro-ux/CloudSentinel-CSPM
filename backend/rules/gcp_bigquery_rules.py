from backend.rules.finding_factory import create_finding


def evaluate_description(dataset):

    findings = []

    if not dataset["description"]:

        findings.append(
            create_finding(
                rule_id="GCP-BQ-001",
                severity="LOW",
                service="BigQuery",
                category="Governance",
                title="Dataset Missing Description",
                description=(
                    f"BigQuery dataset '{dataset['display_name']}' "
                    "does not have a description."
                ),
                recommendation=(
                    "Add a meaningful description to improve "
                    "governance and maintainability."
                ),
                resource_id=dataset["resource_id"],
                evidence={},
                cis_control="Internal",
                mitre_attack="T1580",
                references=[],
            )
        )

    return findings


def evaluate_labels(dataset):

    findings = []

    if not dataset["labels"]:

        findings.append(
            create_finding(
                rule_id="GCP-BQ-002",
                severity="LOW",
                service="BigQuery",
                category="Asset Management",
                title="Dataset Has No Labels",
                description=(
                    f"BigQuery dataset '{dataset['display_name']}' "
                    "does not contain labels."
                ),
                recommendation=(
                    "Apply labels such as environment, owner "
                    "and business unit."
                ),
                resource_id=dataset["resource_id"],
                evidence={
                    "labels": {}
                },
                cis_control="Best Practice",
                mitre_attack="T1580",
                references=[],
            )
        )

    return findings


def evaluate_location(dataset):

    findings = []

    approved_locations = {
        "US",
        "EU",
    }

    if (
        dataset["location"]
        and dataset["location"] not in approved_locations
    ):

        findings.append(
            create_finding(
                rule_id="GCP-BQ-003",
                severity="MEDIUM",
                service="BigQuery",
                category="Compliance",
                title="Dataset In Non-Standard Region",
                description=(
                    f"Dataset '{dataset['display_name']}' "
                    f"is located in '{dataset['location']}'."
                ),
                recommendation=(
                    "Verify that this region complies with "
                    "organizational data residency policies."
                ),
                resource_id=dataset["resource_id"],
                evidence={
                    "location": dataset["location"]
                },
                cis_control="Best Practice",
                mitre_attack="T1537",
                references=[],
            )
        )

    return findings


def evaluate_dataset(dataset):

    findings = []

    findings.extend(
        evaluate_description(dataset)
    )

    findings.extend(
        evaluate_labels(dataset)
    )

    findings.extend(
        evaluate_location(dataset)
    )

    return findings