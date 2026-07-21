import { apiClient } from './client'

export interface Asset {
  asset_type: string
  count: number
  provider: string
}

export interface AssetsResponse {
  success: boolean
  data: Asset[]
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

export interface AssetDetail {
  id: string
  service: string
  resource_type: string
  name: string
  properties: Record<string, unknown>
  relationships: Array<Record<string, unknown>>
}

export async function getAssets(params?: {
  page?: number
  page_size?: number
  provider?: string
  asset_type?: string
  search?: string
}): Promise<AssetsResponse> {
  const response = await apiClient.get('/assets', { params })
  return response.data
}

export async function getAsset(assetId: string): Promise<AssetDetail> {
  const response = await apiClient.get(`/assets/${assetId}`)
  return response.data.data
}
