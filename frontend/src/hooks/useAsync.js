import { useCallback, useEffect, useState } from 'react'

/**
 * Run an async function on mount (and on demand via refetch), tracking
 * loading / error / data states.
 */
export function useAsync(asyncFn, deps = []) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const run = useCallback(() => {
    setLoading(true)
    setError(null)
    return asyncFn()
      .then((result) => setData(result))
      .catch((err) => setError(err.message || 'Request failed'))
      .finally(() => setLoading(false))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)

  useEffect(() => {
    run()
  }, [run])

  return { data, loading, error, refetch: run, setData }
}
