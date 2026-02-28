import * as React from 'react'

interface QueryKey extends Array<unknown> {
  0: string
}

interface UseQueryOptions<T, E = Error> {
  queryKey: QueryKey
  queryFn: () => Promise<T>
  staleTime?: number
  cacheTime?: number
  retry?: number | boolean
  retryDelay?: (attemptIndex: number) => number
  enabled?: boolean
  onSuccess?: (data: T) => void
  onError?: (error: E) => void
}

interface UseQueryResult<T, E = Error> {
  data: T | undefined
  error: E | null
  isLoading: boolean
  isFetching: boolean
  isError: boolean
  isSuccess: boolean
  refetch: () => Promise<void>
}

interface QueryCache {
  data: unknown
  error: unknown
  timestamp: number
  status: 'idle' | 'loading' | 'success' | 'error'
}

const globalCache = new Map<string, QueryCache>()

function getCacheKey(key: QueryKey): string {
  return JSON.stringify(key)
}

export function useQuery<T, E = Error>({
  queryKey,
  queryFn,
  staleTime = 5 * 60 * 1000,
  cacheTime = 10 * 60 * 1000,
  retry = 3,
  retryDelay = (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  enabled = true,
  onSuccess,
  onError,
}: UseQueryOptions<T, E>): UseQueryResult<T, E> {
  const cacheKey = getCacheKey(queryKey)
  const [data, setData] = React.useState<T | undefined>(() => {
    const cached = globalCache.get(cacheKey)
    if (cached && Date.now() - cached.timestamp < staleTime && cached.status === 'success') {
      return cached.data as T
    }
    return undefined
  })
  const [error, setError] = React.useState<E | null>(null)
  const [isLoading, setIsLoading] = React.useState<boolean>(() => {
    const cached = globalCache.get(cacheKey)
    return !cached || Date.now() - cached.timestamp > staleTime
  })
  const [isFetching, setIsFetching] = React.useState(false)
  const [isSuccess, setIsSuccess] = React.useState(false)
  const [isError, setIsError] = React.useState(false)

  const fetchData = React.useCallback(
    async (attempt = 0) => {
      if (!enabled) return

      setIsFetching(true)
      setError(null)

      try {
        const result = await queryFn()
        const cacheData: QueryCache = {
          data: result,
          error: null,
          timestamp: Date.now(),
          status: 'success',
        }
        globalCache.set(cacheKey, cacheData)
        
        setData(result)
        setIsSuccess(true)
        setIsError(false)
        setIsLoading(false)
        setIsFetching(false)
        onSuccess?.(result)

        setTimeout(() => {
          const cached = globalCache.get(cacheKey)
          if (cached && Date.now() - cached.timestamp > cacheTime) {
            globalCache.delete(cacheKey)
          }
        }, cacheTime)

        return result
      } catch (err) {
        const error = err as E
        const shouldRetry = retry === true || (typeof retry === 'number' && attempt < retry)

        if (shouldRetry) {
          const delay = retryDelay(attempt)
          await new Promise((resolve) => setTimeout(resolve, delay))
          return fetchData(attempt + 1)
        }

        const cacheData: QueryCache = {
          data: undefined,
          error: error,
          timestamp: Date.now(),
          status: 'error',
        }
        globalCache.set(cacheKey, cacheData)

        setError(error)
        setIsError(true)
        setIsSuccess(false)
        setIsLoading(false)
        setIsFetching(false)
        onError?.(error)

        return null
      }
    },
    [cacheKey, cacheTime, enabled, onError, onSuccess, queryFn, retry, retryDelay, staleTime]
  )

  const refetch = React.useCallback(async () => {
    setIsLoading(true)
    await fetchData(0)
  }, [fetchData])

  React.useEffect(() => {
    const cached = globalCache.get(cacheKey)
    if (cached && Date.now() - cached.timestamp < staleTime) {
      if (cached.status === 'success') {
        setData(cached.data as T)
        setIsSuccess(true)
        setIsLoading(false)
      } else if (cached.status === 'error') {
        setError(cached.error as E)
        setIsError(true)
        setIsLoading(false)
      }
    }
  }, [cacheKey, staleTime])

  React.useEffect(() => {
    if (enabled) {
      const cached = globalCache.get(cacheKey)
      if (!cached || Date.now() - cached.timestamp > staleTime) {
        fetchData(0)
      }
    }
  }, [cacheKey, enabled, fetchData, staleTime])

  return {
    data,
    error,
    isLoading,
    isFetching,
    isError,
    isSuccess,
    refetch,
  }
}

export function useQueryClient() {
  const invalidateQueries = React.useCallback((queryKey?: QueryKey) => {
    if (queryKey) {
      const key = getCacheKey(queryKey)
      globalCache.delete(key)
    } else {
      globalCache.clear()
    }
  }, [])

  return { invalidateQueries }
}
