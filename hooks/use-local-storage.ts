import * as React from 'react'

type SetValue<T> = (value: T | ((prev: T) => T)) => void

export function useLocalStorage<T>(
  key: string,
  initialValue: T
): [T, SetValue<T>, () => void] {
  const readValue = React.useCallback((): T => {
    if (typeof window === 'undefined') {
      return initialValue
    }

    try {
      const item = window.localStorage.getItem(key)
      return item ? (JSON.parse(item) as T) : initialValue
    } catch (error) {
      console.warn(`Error reading localStorage key "${key}":`, error)
      return initialValue
    }
  }, [initialValue, key])

  const [storedValue, setStoredValue] = React.useState<T>(readValue)

  const setValue: SetValue<T> = React.useCallback(
    (value) => {
      try {
        const valueToStore = value instanceof Function ? value(storedValue) : value
        setStoredValue(valueToStore)
        
        if (typeof window !== 'undefined') {
          window.localStorage.setItem(key, JSON.stringify(valueToStore))
          window.dispatchEvent(new Event('local-storage'))
        }
      } catch (error) {
        console.warn(`Error setting localStorage key "${key}":`, error)
      }
    },
    [key, storedValue]
  )

  const removeValue = React.useCallback(() => {
    try {
      if (typeof window !== 'undefined') {
        window.localStorage.removeItem(key)
        setStoredValue(initialValue)
        window.dispatchEvent(new Event('local-storage'))
      }
    } catch (error) {
      console.warn(`Error removing localStorage key "${key}":`, error)
    }
  }, [initialValue, key])

  React.useEffect(() => {
    setStoredValue(readValue())
  }, [readValue])

  React.useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === key || e.type === 'local-storage') {
        setStoredValue(readValue())
      }
    }
    window.addEventListener('storage', handleStorageChange)
    return () => window.removeEventListener('storage', handleStorageChange)
  }, [key, readValue])

  return [storedValue, setValue, removeValue]
}
