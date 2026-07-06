def normalize_job(job):

    return {

        "cloud": "gcp",

        "service": "Dataflow",

        "resource_type": "Job",

        "resource_id": job.id,

        "name": job.name,

        "display_name": job.name,

        "location": job.location,

        "state": job.current_state.name,

        "type": job.type_.name,

        "created": job.create_time,

        "raw": job,
    }