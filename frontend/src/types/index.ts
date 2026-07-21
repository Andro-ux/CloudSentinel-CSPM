export interface Asset {
  asset_type: string
  count: number
  provider: string
}

export interface Finding {
  id: string
  title: string
  description: string
  severity: string
  category: string
  provider: string
  status: string
  timestamp: string
  recommendation: string
  risk_score: number
}

export interface Risk {
  id: string
  title: string
  description: string
  priority: string
  category: string
  score: number
  affected_assets: string[]
  recommendation: string
}

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

export interface Provider {
  provider_id: string
  name: string
  version: string
  description: string
  supported_services: string[]
  capabilities: string[]
  authentication_methods: string[]
}

export interface PaginationMeta {
  page: number
  page_size: number
  total: number
  has_next: boolean
  has_previous: boolean
}

export interface ApiResponse<T> {
  success: boolean
  data: T
  metadata: {
    generated_at: string
    api_version: string
    pagination?: PaginationMeta
  }
}
