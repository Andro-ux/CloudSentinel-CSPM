import { apiClient } from './client'

export interface Provider {
  provider_id: string
  name: string
  version: string
  description: string
  supported_services: string[]
  capabilities: string[]
  authentication_methods: string[]
}

export interface ProvidersResponse {
  success: boolean
  data: Provider[]
  metadata: {
    total: number
    generated_at: string
    api_version: string
  }
}

export interface Capability {
  provider_id: string
  capabilities: string[]
  supported_services: string[]
  supported_collectors: string[]
  supported_normalizers: string[]
}

export interface CapabilitiesResponse {
  success: boolean
  data: Capability[]
  metadata: {
    total: number
    generated_at: string
    api_version: string
  }
}

export async function getProviders(): Promise<ProvidersResponse> {
  const response = await apiClient.get('/providers')
  return response.data
}

export async function getCapabilities(): Promise<CapabilitiesResponse> {
  const response = await apiClient.get('/capabilities')
  return response.data
}
