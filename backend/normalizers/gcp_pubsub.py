def normalize_topic(topic):

    topic_name = topic.name.split("/")[-1]

    return {

        "cloud": "gcp",

        "service": "Pub/Sub",

        "resource_type": "Topic",

        "resource_id": topic.name,

        "name": topic_name,

        "display_name": topic_name,

        "kms_key": topic.kms_key_name,

        "message_retention_duration":
            topic.message_storage_policy
            if hasattr(topic, "message_storage_policy")
            else None,

        "raw": topic,
    }