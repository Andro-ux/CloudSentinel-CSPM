import { apiClient } from './client'

export interface DashboardResponse {
  success: boolean
  data: {
    summary: {
      total_assets: number
      total_findings: number
      total_facts: number
      total_risks: number
      security_score: {
        overall: number
        grade: string
        dimensions: Record<string, number>
        breakdown: {
          base_score: number
          deductions: Record<string, number>
          total_deductions: number
          final_score: number
        }
      }
      top_risks: Array<Record<string, unknown>>
      dimensions: Record<string, number>
      metrics: Record<string, unknown>
      insights: Array<Record<string, unknown>>
      recommendations: Array<Record<string, unknown>>
      narrative: Record<string, unknown>
      generated_at: string
    }
    security_score: {
      overall: number
      grade: string
      dimensions: Record<string, number>
      breakdown: Record<string, unknown>
    }
    security_dimensions: Record<string, number>
    score_breakdown: Record<string, unknown>
    metrics: Record<string, unknown>
    top_risks: Array<Record<string, unknown>>
    recommendations: Array<Record<string, unknown>>
    insights: Array<Record<string, unknown>>
    executive_narrative: Record<string, unknown>
    generated_at: string
  }
  metadata: {
    generated_at: string
    api_version: string
  }
}

export async function getDashboard(): Promise<DashboardResponse> {
  const response = await apiClient.get('/dashboard')
  return response.data
}
