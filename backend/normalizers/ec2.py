from backend.models.schemas import NormalizedResource

def normalize_security_group(sg: dict) -> NormalizedResource:
    return NormalizedResource(
        resource_id=sg.get('GroupId', ''),
        resource_type='SecurityGroup',
        service='EC2',
        configuration=sg
    )
