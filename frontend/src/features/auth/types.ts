export type UserRole = 'guest' | 'user' | 'admin'

export interface AuthUser {
  id: number
  email: string
  role: UserRole
  created_at: string
}

export interface LoginPayload {
  email: string
  password: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
}
