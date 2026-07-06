from backend.rules.finding_factory import create_finding


def evaluate_job_state(job):

    findings = []

    failed_states = {
        "JOB_STATE_FAILED",
        "JOB_STATE_CANCELLED",
        "JOB_STATE_DRAINED",
        "JOB_STATE_UPDATED",
    }

    if job["state"] in failed_states:

        findings.append(
            create_finding(
                rule_id="GCP-DATAFLOW-001",
                severity="MEDIUM",
                service="Dataflow",
                category="Availability",
                title="Dataflow Job Not Running",
                description=(
                    f"Dataflow job '{job['display_name']}' "
                    f"is currently in state "
                    f"'{job['state']}'."
                ),
                recommendation=(
                    "Review the job logs and determine "
                    "why execution stopped."
                ),
                resource_id=job["resource_id"],
                evidence={
                    "state": job["state"]
                },
                cis_control="Best Practice",
                mitre_attack="T1499",
                references=[],
            )
        )

    return findings


def evaluate_batch_job(job):

    findings = []

    if job["type"] == "JOB_TYPE_BATCH":

        findings.append(
            create_finding(
                rule_id="GCP-DATAFLOW-002",
                severity="LOW",
                service="Dataflow",
                category="Inventory",
                title="Batch Dataflow Job",
                description=(
                    f"Job '{job['display_name']}' "
                    "is a batch job."
                ),
                recommendation=(
                    "Verify batch workloads meet "
                    "organizational scheduling policies."
                ),
                resource_id=job["resource_id"],
                evidence={
                    "type": job["type"]
                },
                cis_control="Internal",
                mitre_attack="T1580",
                references=[],
            )
        )

    return findings


def evaluate_job(job):

    findings = []

    findings.extend(
        evaluate_job_state(job)
    )

    findings.extend(
        evaluate_batch_job(job)
    )

    return findings