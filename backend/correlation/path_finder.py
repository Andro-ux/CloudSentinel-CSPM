from collections import deque


class PathFinder:

    def bfs(self, graph, start):

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

    def dfs(self, graph, start):

        visited = set()

        stack = [(start, [start])]

        paths = []

        while stack:

            node, path = stack.pop()

            if node in visited:

                continue

            visited.add(node)

            neighbours = graph.get(node, [])

            if not neighbours:

                paths.append(path)

                continue

            for nxt, _ in neighbours:

                stack.append(

                    (

                        nxt,

                        path + [nxt]

                    )

                )

        return paths
