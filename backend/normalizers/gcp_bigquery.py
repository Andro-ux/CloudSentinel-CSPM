def normalize_dataset(dataset):

    return {

        "service": "BigQuery",

        "resource_type": "Dataset",

        "resource_id": dataset.dataset_id,

        "name": dataset.dataset_id,

        "display_name": dataset.full_dataset_id,

        "location": dataset.location,

        "description": dataset.description or "",

        "labels": dict(dataset.labels or {}),

        "raw": dataset,
    }