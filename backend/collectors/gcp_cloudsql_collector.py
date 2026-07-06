from backend.utils.gcp import (
    get_sqladmin_client,
    get_project_id,
)


def collect_sql_instances():

    sql = get_sqladmin_client()

    project = get_project_id()

    response = (
        sql.instances()
        .list(project=project)
        .execute()
    )

    return response.get("items", [])