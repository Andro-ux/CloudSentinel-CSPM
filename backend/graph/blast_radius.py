class BlastRadius:

    def calculate(

        self,

        paths

    ):

        radius = {}

        for path in paths:

            if not path:

                continue

            root = path[0]

            radius.setdefault(

                root,

                0

            )

            radius[root] += len(path) - 1

        return radius