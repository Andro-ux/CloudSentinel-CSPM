import { apiClient } from './client'

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

export interface FindingsResponse {
  success: boolean
  data: Finding[]
  metadata: {
    pagination: {
      page: number
      page_size: number
      total: number
      has_next: boolean
      has_previous: boolean
    }
    generated_at: string
    api_version: string
  }
}

export async function getFindings(params?: {
  page?: number
  page_size?: number
  severity?: string
  category?: string
  provider?: string
  asset?: string
}): Promise<FindingsResponse> {
  const response = await apiClient.get('/findings', { params })
  return response.data
}
