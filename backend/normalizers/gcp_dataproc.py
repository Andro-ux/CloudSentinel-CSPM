def normalize_cluster(cluster):

    config = cluster.config

    gce = config.gce_cluster_config

    return {

        "cloud": "gcp",

        "service": "Dataproc",

        "resource_type": "Cluster",

        "resource_id": cluster.cluster_uuid,

        "name": cluster.cluster_name,

        "display_name": cluster.cluster_name,

        "region": cluster.cluster_name.split("/")[-1]
        if "/" in cluster.cluster_name
        else "",

        "state": cluster.status.state.name,

        "image_version": config.software_config.image_version,

        "internal_ip_only": gce.internal_ip_only,

        "shielded_vm": (
            gce.shielded_instance_config.enable_secure_boot
            if gce.shielded_instance_config
            else False
        ),

        "labels": dict(cluster.labels),

        "kms_key": (
            config.encryption_config.gce_pd_kms_key_name
            if config.encryption_config
            else ""
        ),

        "raw": cluster,
    }