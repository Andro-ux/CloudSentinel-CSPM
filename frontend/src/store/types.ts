export interface User {
  id: number
  username: string
  email?: string
  organization_id?: number
  role_ids: string[]
}

export interface TokenPair {
  access_token: string
  refresh_token: string
}
