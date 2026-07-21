import { describe, it, expect } from 'vitest'
import { formatDate, formatNumber } from '../utils/format'

describe('format utilities', () => {
  it('formats dates correctly', () => {
    const result = formatDate('2024-01-15T10:30:00Z')
    expect(result).toContain('Jan')
    expect(result).toContain('15')
    expect(result).toContain('2024')
  })

  it('formats numbers with commas', () => {
    expect(formatNumber(1000)).toBe('1,000')
    expect(formatNumber(1000000)).toBe('1,000,000')
  })
})
