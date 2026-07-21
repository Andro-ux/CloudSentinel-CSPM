from collections import deque


class GraphTraversal:

    def bfs(

        self,

        graph,

        start

    ):

        visited = set()

        queue = deque()

        queue.append(

            (
                start,
                [start]
            )

        )

        paths = []

        while queue:

            node, path = queue.popleft()

            if node in visited:

                continue

            visited.add(node)

            paths.append(path)

            for neighbour, _ in graph.get(

                node,

                []

            ):

                if neighbour not in visited:

                    queue.append(

                        (

                            neighbour,

                            path + [neighbour]

                        )

                    )

        return paths