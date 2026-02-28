import * as React from 'react'

interface RateLimitConfig {
  maxRequests: number
  windowMs: number
}

interface RateLimitState {
  count: number
  resetTime: number
}

export function useRateLimiter(config: RateLimitConfig) {
  const [state, setState] = React.useState<RateLimitState>({
    count: 0,
    resetTime: 0,
  })

  const checkLimit = React.useCallback((): boolean => {
    const now = Date.now()
    
    if (now > state.resetTime) {
      setState({
        count: 1,
        resetTime: now + config.windowMs,
      })
      return true
    }

    if (state.count >= config.maxRequests) {
      return false
    }

    setState(prev => ({
      count: prev.count + 1,
      resetTime: prev.resetTime,
    }))
    return true
  }, [config.maxRequests, config.windowMs, state.count, state.resetTime])

  const getRemainingTime = React.useCallback((): number => {
    const now = Date.now()
    if (now > state.resetTime) return 0
    return Math.ceil((state.resetTime - now) / 1000)
  }, [state.resetTime])

  const isLimited = React.useCallback((): boolean => {
    const now = Date.now()
    if (now > state.resetTime) return false
    return state.count >= config.maxRequests
  }, [config.maxRequests, state.count, state.resetTime])

  return {
    checkLimit,
    getRemainingTime,
    isLimited,
    remaining: Math.max(0, config.maxRequests - state.count),
  }
}
