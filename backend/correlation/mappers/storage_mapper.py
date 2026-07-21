class StorageMapper:

    def map(

        self,

        assets,

        builder

    ):

        for asset in assets:

            if asset.service != "Storage":

                continue

            project = asset.properties.get(
                "project"
            )

            if not project:

                continue

            builder.connect(

                asset.id,

                project,

                "BELONGS_TO"

            )