class ReachabilityEngine:

    def reachable(

        self,

        traversal,

        graph,

        sources

    ):

        reachable = []

        for source in sources:

            reachable.extend(

                traversal.bfs(

                    graph,

                    source

                )

            )

        return reachable