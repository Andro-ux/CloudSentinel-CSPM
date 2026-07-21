from fastapi import APIRouter, Depends, HTTPException
from backend.api.dependencies import get_scan_service
from backend.services.scan_service import ScanService


router = APIRouter()


@router.get(
    "/graph",
    response_model=dict,
    tags=["Graph"],
    summary="Get knowledge graph",
    description="Returns the knowledge graph including nodes, edges, and metadata.",
)
def get_graph(scan_service: ScanService = Depends(get_scan_service)):
    try:
        result = scan_service.run_scan()
        generated_at = None
        if result and result.dashboard:
            generated_at = result.dashboard.generated_at.isoformat()
        elif result:
            generated_at = __import__('datetime').datetime.utcnow().isoformat()
        if not result or not result.relationships:
            return {
                "success": True,
                "data": {
                    "nodes": [],
                    "edges": [],
                    "metadata": {
                        "total_nodes": 0,
                        "total_edges": 0,
                        "generated_at": generated_at,
                        "api_version": "v1",
                    },
                },
            }
        nodes = []
        edges = []
        for rel in result.relationships:
            edges.append({
                "source": rel.source,
                "target": rel.target,
                "relation": rel.relation,
                "provider": rel.provider,
                "confidence": rel.confidence,
            })
        return {
            "success": True,
            "data": {
                "nodes": nodes,
                "edges": edges,
                "metadata": {
                    "total_nodes": len(nodes),
                    "total_edges": len(edges),
                    "generated_at": generated_at,
                    "api_version": "v1",
                },
            },
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
