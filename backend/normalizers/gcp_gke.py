def normalize_cluster(cluster):

    endpoint = getattr(cluster, "endpoint", "")

    return {

        "cloud": "gcp",

        "service": "GKE",

        "resource_type": "Cluster",

        "resource_id": cluster.id,

        "name": cluster.name,

        "location": cluster.location,

        "status": cluster.status.name,

        "endpoint": endpoint,

        "private_cluster": cluster.private_cluster_config.enable_private_nodes
        if cluster.private_cluster_config
        else False,

        "network_policy": cluster.network_policy.enabled
        if cluster.network_policy
        else False,

        "shielded_nodes": cluster.shielded_nodes.enabled
        if cluster.shielded_nodes
        else False,

        "workload_identity": bool(
            cluster.workload_identity_config.workload_pool
        )
        if cluster.workload_identity_config
        else False,

        "logging_service": cluster.logging_service,

        "monitoring_service": cluster.monitoring_service,

        "node_pools": len(cluster.node_pools),

        "raw": cluster,
    }