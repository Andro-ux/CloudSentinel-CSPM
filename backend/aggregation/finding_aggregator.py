from collections import defaultdict


class FindingAggregator:

    def aggregate(self, findings):

        groups = defaultdict(list)

        for finding in findings:

            key = (
                finding["rule_id"],
                finding["service"],
                finding["severity"]
            )

            groups[key].append(finding)

        aggregated = []

        for (_, _, _), items in groups.items():

            if len(items) == 1:
                aggregated.append(items[0])
                continue

            first = items[0]

            aggregated.append({

                **first,

                "affected_assets": len(items),

                "affected_resource_ids": [
                    i["resource_id"]
                    for i in items
                ],

                "affected_titles": [
                    i["description"]
                    for i in items
                ]

            })

        return aggregated