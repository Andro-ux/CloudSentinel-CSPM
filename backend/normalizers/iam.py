from backend.models.schemas import NormalizedResource

def normalize_iam_user(user: dict) -> NormalizedResource:
    return NormalizedResource(
        resource_id=user.get('Arn', ''),
        resource_type='IAMUser',
        service='IAM',
        configuration={
            'UserName': user.get('UserName'),
            'AttachedPolicies': user.get('AttachedPolicies', []),
            'InlinePolicies': user.get('InlinePolicies', [])
        }
    )

def normalize_credential_report(report: list) -> list[NormalizedResource]:
    resources = []
    for row in report:
        if row.get('arn'):
            resources.append(NormalizedResource(
                resource_id=row['arn'],
                resource_type='IAMUserCredentialInfo',
                service='IAM',
                configuration=row
            ))
    return resources
