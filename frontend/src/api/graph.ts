import { apiClient } from './client'

export interface GraphNode {
  id: string
  label: string
  type: string
  properties: Record<string, unknown>
}

export interface GraphEdge {
  source: string
  target: string
  relation: string
  provider: string
  confidence: number
}

export interface GraphResponse {
  success: boolean
  data: {
    nodes: GraphNode[]
    edges: GraphEdge[]
    metadata: {
      total_nodes: number
      total_edges: number
      generated_at: string
      api_version: string
    }
  }
}

export async function getGraph(): Promise<GraphResponse> {
  const response = await apiClient.get('/graph')
  return response.data
}
