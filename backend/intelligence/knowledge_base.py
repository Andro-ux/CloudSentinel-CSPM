KNOWLEDGE_BASE = {

    "PUBLIC_VM": {

        "business_impact":
            "Internet-facing virtual machines significantly increase the external attack surface and are common entry points for ransomware, cryptomining and initial access attacks.",

        "likelihood":
            "High",

        "estimated_remediation":
            "15-30 minutes",

        "frameworks": [

            "CIS GCP 4.1",

            "MITRE T1190",

            "NIST PR.AC"

        ],

        "priority": "Immediate"

    },

    "PUBLIC_BUCKET": {

        "business_impact":
            "Public storage buckets can expose sensitive or regulated information to unauthorized users.",

        "likelihood":
            "Critical",

        "estimated_remediation":
            "10 minutes",

        "frameworks": [

            "CIS GCP 5.1",

            "MITRE T1530",

            "NIST PR.DS"

        ],

        "priority": "Immediate"

    },

    "FLOW_LOG_DISABLED": {

        "business_impact":
            "Missing network telemetry limits threat detection, incident response and forensic investigations.",

        "likelihood":
            "Medium",

        "estimated_remediation":
            "20 minutes",

        "frameworks": [

            "CIS GCP 3.9",

            "NIST DE.CM"

        ],

        "priority": "High"

    },

}