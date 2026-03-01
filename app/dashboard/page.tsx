"use client"

import type React from "react"

import { useEffect, useState, useTransition, useMemo } from "react"
// import { useUser, useClerk } from "@clerk/nextjs"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Skeleton } from "@/components/ui/skeleton"
import { useDebounce } from "@/hooks/use-debounce"
import { useRateLimiter } from "@/hooks/use-rate-limiter"
import {
  Shield,
  Scan,
  LogOut,
  AlertCircle,
  Activity,
  Clock,
  CheckCircle,
  XCircle,
  Loader2,
  TrendingUp,
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  ChevronLeft,
  ChevronRight,
  Search,
  Zap,
  Target,
  ShieldAlert,
  ShieldCheck,
  LayoutDashboard,
} from "lucide-react"
import Link from "next/link"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

interface Scan {
  id: string
  target_url: string
  scan_status: string
  started_at: string
  completed_at: string | null
  total_vulnerabilities: number
  critical_count: number
  high_count: number
  medium_count: number
  low_count: number
}

type SortField = "started_at" | "scan_status" | "critical_count" | "high_count" | "total_vulnerabilities"
type SortDirection = "asc" | "desc"
type FilterStatus = "all" | "completed" | "running" | "failed" | "pending"

const ITEMS_PER_PAGE = 10

const MOCK_USER = { fullName: "Local User", primaryEmailAddress: { emailAddress: "local@example.com" } }

export default function DashboardPage() {
  const user = MOCK_USER
  const isLoaded = true
  const isSignedIn = true
  const signOut = () => router.push("/")
  const router = useRouter()
  const [targetUrl, setTargetUrl] = useState("")
  const [scanning, setScanning] = useState(false)
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")
  const [scans, setScans] = useState<Scan[]>([])
  const [loadingScans, setLoadingScans] = useState(true)
  const [isPending, startTransition] = useTransition()
  const [navigatingScanId, setNavigatingScanId] = useState<string | null>(null)

  // Sorting state
  const [sortField, setSortField] = useState<SortField>("started_at")
  const [sortDirection, setSortDirection] = useState<SortDirection>("desc")

  // Filtering state
  const [filterStatus, setFilterStatus] = useState<FilterStatus>("all")

  // Pagination state
  const [currentPage, setCurrentPage] = useState(1)

  const debouncedUrl = useDebounce(targetUrl, 500)

  const rateLimiter = useRateLimiter({
    maxRequests: 5,
    windowMs: 60 * 1000,
  })

  const canSubmit = useMemo(() => {
    if (!debouncedUrl || scanning) return false
    return !rateLimiter.isLimited()
  }, [debouncedUrl, scanning, rateLimiter])

  // Filter, sort, and paginate scans
  const processedScans = useMemo(() => {
    let filtered = [...scans]

    // Apply filter
    if (filterStatus !== "all") {
      filtered = filtered.filter(scan => scan.scan_status === filterStatus)
    }

    // Apply sort
    filtered.sort((a, b) => {
      let aVal: string | number
      let bVal: string | number

      switch (sortField) {
        case "started_at":
          aVal = new Date(a.started_at).getTime()
          bVal = new Date(b.started_at).getTime()
          break
        case "scan_status":
          aVal = a.scan_status
          bVal = b.scan_status
          break
        case "critical_count":
          aVal = a.critical_count
          bVal = b.critical_count
          break
        case "high_count":
          aVal = a.high_count
          bVal = b.high_count
          break
        case "total_vulnerabilities":
          aVal = a.total_vulnerabilities
          bVal = b.total_vulnerabilities
          break
        default:
          aVal = a.started_at
          bVal = b.started_at
      }

      if (aVal < bVal) return sortDirection === "asc" ? -1 : 1
      if (aVal > bVal) return sortDirection === "asc" ? 1 : -1
      return 0
    })

    return filtered
  }, [scans, filterStatus, sortField, sortDirection])

  const totalPages = Math.ceil(processedScans.length / ITEMS_PER_PAGE)
  const paginatedScans = useMemo(() => {
    const start = (currentPage - 1) * ITEMS_PER_PAGE
    return processedScans.slice(start, start + ITEMS_PER_PAGE)
  }, [processedScans, currentPage])

  useEffect(() => {
    // Auth disabled for local
  }, [isLoaded, isSignedIn, router])

  useEffect(() => {
    if (isSignedIn && user) {
      const savedScrollPos = sessionStorage.getItem("dashboard-scrollPos")
      if (savedScrollPos) {
        setTimeout(() => {
          window.scrollTo(0, parseInt(savedScrollPos, 10))
          sessionStorage.removeItem("dashboard-scrollPos")
        }, 100)
      }
      fetchScans()
    }
  }, [isSignedIn, user])

  useEffect(() => {
    const handleBeforeUnload = () => {
      sessionStorage.setItem("dashboard-scrollPos", window.scrollY.toString())
    }
    window.addEventListener("beforeunload", handleBeforeUnload)
    return () => window.removeEventListener("beforeunload", handleBeforeUnload)
  }, [])

  // ... fetchScans and handleStartScan ...

  async function fetchScans() {
    try {
      const response = await fetch("/api/scans")
      if (response.ok) {
        const data = await response.json()
        setScans(data.scans || [])
      }
    } catch (err) {
      console.error("[v0] Failed to fetch scans:", err)
    } finally {
      setLoadingScans(false)
    }
  }

  async function handleStartScan(e: React.FormEvent) {
    e.preventDefault()
    setError("")
    setSuccess("")

    if (!rateLimiter.checkLimit()) {
      const remaining = rateLimiter.getRemainingTime()
      setError(`Rate limit exceeded. Please wait ${remaining} seconds before starting another scan.`)
      return
    }

    setScanning(true)

    const optimisticScan: Scan = {
      id: `temp-${Date.now()}`,
      target_url: targetUrl,
      scan_status: "pending",
      started_at: new Date().toISOString(),
      completed_at: null,
      total_vulnerabilities: 0,
      critical_count: 0,
      high_count: 0,
      medium_count: 0,
      low_count: 0,
    }

    setScans(prev => [optimisticScan, ...prev])

    try {
      try {
        new URL(targetUrl)
      } catch {
        setScans(prev => prev.filter(s => s.id !== optimisticScan.id))
        throw new Error("Please enter a valid URL")
      }

      const response = await fetch("/api/scans/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: targetUrl }),
      })

      const data = await response.json()

      if (!response.ok) {
        setScans(prev => prev.filter(s => s.id !== optimisticScan.id))
        throw new Error(data.error || "Failed to start scan")
      }

      setScans(prev =>
        prev.map(s =>
          s.id === optimisticScan.id
            ? { ...s, id: data.scanId, scan_status: "running" }
            : s
        )
      )

      setSuccess("Scan started successfully!")
      setTargetUrl("")

      setTimeout(() => {
        router.push(`/scan/${data.scanId}`)
      }, 1500)
    } catch (err) {
      setScans(prev => prev.filter(s => s.id !== optimisticScan.id))
      setError(err instanceof Error ? err.message : "Failed to start scan")
    } finally {
      setScanning(false)
    }
  }

  if (!isLoaded || !user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
        <Loader2 className="h-8 w-8 animate-spin text-emerald-400" />
      </div>
    )
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="h-4 w-4 text-emerald-400" />
      case "running":
        return <Activity className="h-4 w-4 text-blue-400 animate-pulse" />
      case "failed":
        return <XCircle className="h-4 w-4 text-red-400" />
      default:
        return <Clock className="h-4 w-4 text-yellow-400" />
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case "completed":
        return "Completed"
      case "running":
        return "Scanning..."
      case "failed":
        return "Failed"
      default:
        return "Pending"
    }
  }

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(prev => prev === "asc" ? "desc" : "asc")
    } else {
      setSortField(field)
      setSortDirection("desc")
    }
    setCurrentPage(1)
  }

  const handleFilterChange = (value: string) => {
    setFilterStatus(value as FilterStatus)
    setCurrentPage(1)
  }

  const getSortIcon = (field: SortField) => {
    if (sortField !== field) return <ArrowUpDown className="h-4 w-4 ml-1" />
    return sortDirection === "asc" ? (
      <ArrowUp className="h-4 w-4 ml-1 text-emerald-400" />
    ) : (
      <ArrowDown className="h-4 w-4 ml-1 text-emerald-400" />
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      {/* Navigation */}
      <nav className="border-b border-slate-800 bg-slate-900/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-8">
              <Link href="/dashboard" className="flex items-center gap-3 group">
                <div className="p-2 bg-emerald-500/10 rounded-lg group-hover:bg-emerald-500/20 transition-colors">
                  <Shield className="h-7 w-7 text-emerald-400" />
                </div>
                <span className="text-xl font-bold text-slate-100">VulnScan AI</span>
              </Link>
              <div className="hidden md:flex items-center gap-1">
                <Button variant="ghost" size="sm" className="text-emerald-400 bg-emerald-500/10">
                  <LayoutDashboard className="h-4 w-4 mr-2" />
                  Dashboard
                </Button>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="hidden sm:block text-sm text-slate-400">
                <span className="text-slate-300">{user.fullName || user.primaryEmailAddress?.emailAddress}</span>
              </div>
              <Button variant="ghost" size="sm" onClick={() => signOut()} className="text-slate-400 hover:text-slate-100 hover:bg-slate-800">
                <LogOut className="h-4 w-4 mr-2" />
                <span className="hidden sm:inline">Logout</span>
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Scan Input Section */}
        {/* Scan Input Section */}
        <div className="bg-[#0a0a0e] border border-slate-800/60 rounded-xl overflow-hidden shadow-2xl shadow-purple-900/10">
          <div className="h-10 bg-[#15151b] border-b border-slate-800/80 flex items-center px-4 shrink-0">
            <div className="flex gap-2 w-1/3">
              <div className="w-3 h-3 rounded-full bg-red-500/80"></div>
              <div className="w-3 h-3 rounded-full bg-yellow-500/80"></div>
              <div className="w-3 h-3 rounded-full bg-green-500/80"></div>
            </div>
            <div className="w-1/3 text-center">
              <span className="text-xs text-slate-400 font-mono">vulnscan-launcher.exe</span>
            </div>
          </div>

          <div className="p-8">
            <div className="mb-8">
              <h2 className="text-xl font-bold text-slate-100 flex items-center gap-3">
                <span className="text-purple-500">{">_"}</span>
                Start New Vulnerability Scan
              </h2>
              <p className="text-sm text-slate-500 font-mono mt-2">
                Enter a target URL to initiate automated OWASP Top 10 analysis sequence...
              </p>
            </div>

            <form onSubmit={handleStartScan} className="space-y-6">
              {error && (
                <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-lg flex items-start gap-3 text-red-400 font-mono text-sm">
                  <AlertCircle className="h-5 w-5 shrink-0 mt-0.5" />
                  <p>{error}</p>
                </div>
              )}

              {success && (
                <div className="p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-lg flex items-start gap-3 text-emerald-400 font-mono text-sm">
                  <CheckCircle className="h-5 w-5 shrink-0 mt-0.5" />
                  <p>{success}</p>
                </div>
              )}

              <div className="flex flex-col sm:flex-row gap-4">
                <div className="relative flex-1">
                  <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-500" />
                  <input
                    id="url-input"
                    type="url"
                    placeholder="https://target-system.com"
                    value={targetUrl}
                    onChange={(e) => setTargetUrl(e.target.value)}
                    required
                    className="w-full h-12 pl-12 pr-4 bg-[#111116] border border-slate-700/60 rounded-lg text-slate-100 placeholder:text-slate-600 font-mono focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500 transition-all font-medium"
                    disabled={scanning}
                  />
                </div>
                <button
                  type="submit"
                  disabled={scanning || !canSubmit}
                  className="h-12 px-8 bg-purple-600 hover:bg-purple-500 disabled:bg-slate-800 disabled:text-slate-500 text-white rounded-lg font-bold tracking-wide flex items-center justify-center gap-2 transition-colors disabled:cursor-not-allowed border border-purple-500/50 disabled:border-slate-700 shadow-[0_0_15px_rgba(147,51,234,0.3)] disabled:shadow-none"
                >
                  {scanning ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      INITIATING...
                    </>
                  ) : rateLimiter.isLimited() ? (
                    <>
                      <Clock className="h-4 w-4" />
                      WAIT {rateLimiter.getRemainingTime()}S
                    </>
                  ) : (
                    <>
                      <Zap className="h-4 w-4" />
                      EXECUTE SCAN
                    </>
                  )}
                </button>
              </div>

              {rateLimiter.isLimited() && (
                <p className="text-xs text-slate-500 font-mono flex items-center gap-2">
                  <Clock className="h-3 w-3" />
                  Rate limit active: {rateLimiter.remaining}/5 scans remaining this minute.
                </p>
              )}
            </form>
          </div>
        </div>

        {/* Stats Overview */}
        <div className="grid md:grid-cols-4 gap-4">
          {/* Total Scans Card */}
          <Card className="border-slate-800 bg-slate-900/60 backdrop-blur hover:bg-slate-900/80 transition-colors">
            <CardContent className="p-5">
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <p className="text-sm font-medium text-slate-400">Total Scans</p>
                  <p className="text-3xl font-bold text-slate-100">
                    {loadingScans ? <Skeleton className="h-9 w-16 bg-slate-700" /> : processedScans.length}
                  </p>
                </div>
                <div className="p-3 bg-emerald-500/10 rounded-xl">
                  <TrendingUp className="h-6 w-6 text-emerald-400" />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Critical Vulnerabilities Card */}
          <Card className="border-slate-800 bg-slate-900/60 backdrop-blur hover:bg-slate-900/80 transition-colors">
            <CardContent className="p-5">
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <p className="text-sm font-medium text-slate-400">Critical Issues</p>
                  <p className="text-3xl font-bold text-red-400">
                    {loadingScans ? <Skeleton className="h-9 w-16 bg-slate-700" /> : processedScans.reduce((sum, scan) => sum + scan.critical_count, 0)}
                  </p>
                </div>
                <div className="p-3 bg-red-500/10 rounded-xl">
                  <ShieldAlert className="h-6 w-6 text-red-400" />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* High Priority Card */}
          <Card className="border-slate-800 bg-slate-900/60 backdrop-blur hover:bg-slate-900/80 transition-colors">
            <CardContent className="p-5">
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <p className="text-sm font-medium text-slate-400">High Priority</p>
                  <p className="text-3xl font-bold text-orange-400">
                    {loadingScans ? <Skeleton className="h-9 w-16 bg-slate-700" /> : processedScans.reduce((sum, scan) => sum + scan.high_count, 0)}
                  </p>
                </div>
                <div className="p-3 bg-orange-500/10 rounded-xl">
                  <AlertCircle className="h-6 w-6 text-orange-400" />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Total Vulnerabilities Card */}
          <Card className="border-slate-800 bg-slate-900/60 backdrop-blur hover:bg-slate-900/80 transition-colors">
            <CardContent className="p-5">
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <p className="text-sm font-medium text-slate-400">Total Vulnerabilities</p>
                  <p className="text-3xl font-bold text-slate-100">
                    {loadingScans ? <Skeleton className="h-9 w-16 bg-slate-700" /> : processedScans.reduce((sum, scan) => sum + scan.total_vulnerabilities, 0)}
                  </p>
                </div>
                <div className="p-3 bg-blue-500/10 rounded-xl">
                  <ShieldCheck className="h-6 w-6 text-blue-400" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Recent Scans */}
        <Card className="border-slate-800 bg-slate-900/60 backdrop-blur shadow-lg shadow-black/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
            <div className="space-y-1">
              <CardTitle className="text-slate-100 flex items-center gap-2">
                <Target className="h-5 w-5 text-emerald-400" />
                Recent Scans
              </CardTitle>
              <CardDescription className="text-slate-400">View your scan history and results</CardDescription>
            </div>
            <Select value={filterStatus} onValueChange={handleFilterChange}>
              <SelectTrigger className="w-[180px] bg-slate-800/50 border-slate-700 text-slate-100">
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent className="bg-slate-800 border-slate-700">
                <SelectItem value="all" className="text-slate-100">All Statuses</SelectItem>
                <SelectItem value="completed" className="text-slate-100">Completed</SelectItem>
                <SelectItem value="running" className="text-slate-100">Running</SelectItem>
                <SelectItem value="failed" className="text-slate-100">Failed</SelectItem>
                <SelectItem value="pending" className="text-slate-100">Pending</SelectItem>
              </SelectContent>
            </Select>
          </CardHeader>
          <CardContent>
            {loadingScans ? (
              /* Skeleton Loader for Table */
              <div className="space-y-3">
                <div className="flex items-center gap-4 p-4">
                  <Skeleton className="h-4 w-24 bg-slate-700" />
                  <Skeleton className="h-4 w-20 bg-slate-700" />
                  <Skeleton className="h-4 w-48 bg-slate-700" />
                  <Skeleton className="h-4 w-16 bg-slate-700 ml-auto" />
                  <Skeleton className="h-4 w-12 bg-slate-700" />
                  <Skeleton className="h-4 w-12 bg-slate-700" />
                </div>
                {[...Array(5)].map((_, i) => (
                  <div key={i} className="flex items-center gap-4 p-4 border-t border-slate-800">
                    <Skeleton className="h-4 w-24 bg-slate-700" />
                    <Skeleton className="h-4 w-20 bg-slate-700" />
                    <Skeleton className="h-4 w-48 bg-slate-700" />
                    <Skeleton className="h-6 w-12 bg-slate-700 ml-auto rounded" />
                    <Skeleton className="h-6 w-12 bg-slate-700 rounded" />
                    <Skeleton className="h-4 w-12 bg-slate-700" />
                  </div>
                ))}
              </div>
            ) : processedScans.length === 0 ? (
              /* Empty State */
              <div className="flex flex-col items-center justify-center py-16 px-4">
                <div className="relative mb-6">
                  <div className="absolute inset-0 bg-emerald-500/10 rounded-full blur-2xl"></div>
                  <div className="relative p-6 bg-slate-800/50 rounded-2xl border border-slate-700">
                    <Scan className="h-16 w-16 text-slate-600" />
                  </div>
                </div>
                <h3 className="text-xl font-semibold text-slate-200 mb-2">
                  {filterStatus !== "all" ? "No scans found" : "No scans yet"}
                </h3>
                <p className="text-slate-400 text-center max-w-md mb-6">
                  {filterStatus !== "all"
                    ? `You don't have any ${filterStatus} scans. Try changing the filter or start a new scan.`
                    : "Start your first vulnerability scan to discover potential security issues in your web applications."}
                </p>
                {filterStatus === "all" && (
                  <Button
                    onClick={() => document.getElementById('url-input')?.focus()}
                    className="bg-emerald-600 hover:bg-emerald-700 text-white"
                  >
                    <Zap className="h-4 w-4 mr-2" />
                    Start Your First Scan
                  </Button>
                )}
                {filterStatus !== "all" && (
                  <Button
                    variant="outline"
                    onClick={() => setFilterStatus("all")}
                    className="border-slate-700 text-slate-300 hover:bg-slate-800 hover:text-slate-100"
                  >
                    Clear Filter
                  </Button>
                )}
              </div>
            ) : (
              <>
                <Table>
                  <TableHeader>
                    <TableRow className="border-slate-700 hover:bg-slate-800/50">
                      <TableHead
                        className="text-slate-300 cursor-pointer hover:text-emerald-400"
                        onClick={() => handleSort("started_at")}
                      >
                        <div className="flex items-center">
                          Date {getSortIcon("started_at")}
                        </div>
                      </TableHead>
                      <TableHead
                        className="text-slate-300 cursor-pointer hover:text-emerald-400"
                        onClick={() => handleSort("scan_status")}
                      >
                        <div className="flex items-center">
                          Status {getSortIcon("scan_status")}
                        </div>
                      </TableHead>
                      <TableHead className="text-slate-300">Target URL</TableHead>
                      <TableHead
                        className="text-slate-300 cursor-pointer hover:text-emerald-400 text-right"
                        onClick={() => handleSort("critical_count")}
                      >
                        <div className="flex items-center justify-end">
                          Critical {getSortIcon("critical_count")}
                        </div>
                      </TableHead>
                      <TableHead
                        className="text-slate-300 cursor-pointer hover:text-emerald-400 text-right"
                        onClick={() => handleSort("high_count")}
                      >
                        <div className="flex items-center justify-end">
                          High {getSortIcon("high_count")}
                        </div>
                      </TableHead>
                      <TableHead
                        className="text-slate-300 cursor-pointer hover:text-emerald-400 text-right"
                        onClick={() => handleSort("total_vulnerabilities")}
                      >
                        <div className="flex items-center justify-end">
                          Total {getSortIcon("total_vulnerabilities")}
                        </div>
                      </TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {paginatedScans.map((scan) => (
                      <TableRow
                        key={scan.id}
                        onClick={() => {
                          setNavigatingScanId(scan.id)
                          startTransition(() => {
                            router.push(`/scan/${scan.id}`)
                          })
                        }}
                        className="border-slate-800 hover:bg-slate-800/60 cursor-pointer transition-colors group"
                      >
                        <TableCell className="text-slate-300 font-mono text-sm">
                          {new Date(scan.started_at).toLocaleString()}
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            {navigatingScanId === scan.id ? (
                              <Loader2 className="h-4 w-4 text-emerald-400 animate-spin" />
                            ) : (
                              getStatusIcon(scan.scan_status)
                            )}
                            <span className="text-slate-300 group-hover:text-slate-100 transition-colors">
                              {navigatingScanId === scan.id ? "Loading..." : getStatusText(scan.scan_status)}
                            </span>
                          </div>
                        </TableCell>
                        <TableCell className="text-slate-100 font-medium max-w-[300px] truncate">
                          {scan.target_url}
                        </TableCell>
                        <TableCell className="text-right">
                          {scan.critical_count > 0 ? (
                            <span className="px-2.5 py-1 bg-red-500/15 border border-red-500/30 rounded-md text-xs font-medium text-red-400">
                              {scan.critical_count}
                            </span>
                          ) : (
                            <span className="text-slate-500">0</span>
                          )}
                        </TableCell>
                        <TableCell className="text-right">
                          {scan.high_count > 0 ? (
                            <span className="px-2.5 py-1 bg-orange-500/15 border border-orange-500/30 rounded-md text-xs font-medium text-orange-400">
                              {scan.high_count}
                            </span>
                          ) : (
                            <span className="text-slate-500">0</span>
                          )}
                        </TableCell>
                        <TableCell className="text-right text-slate-300 font-medium">
                          {scan.total_vulnerabilities}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>

                {/* Pagination */}
                {totalPages > 1 && (
                  <div className="flex items-center justify-between mt-6 pt-4 border-t border-slate-700">
                    <div className="text-sm text-slate-400">
                      Showing <span className="text-slate-300">{(currentPage - 1) * ITEMS_PER_PAGE + 1}</span> to{" "}
                      <span className="text-slate-300">{Math.min(currentPage * ITEMS_PER_PAGE, processedScans.length)}</span> of{" "}
                      <span className="text-slate-300">{processedScans.length}</span> scans
                    </div>
                    <div className="flex items-center gap-1">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                        disabled={currentPage === 1}
                        className="border-slate-700 text-slate-300 hover:bg-slate-800 hover:text-slate-100"
                      >
                        <ChevronLeft className="h-4 w-4" />
                      </Button>
                      {Array.from({ length: totalPages }, (_, i) => i + 1).map(page => (
                        <Button
                          key={page}
                          variant={page === currentPage ? "default" : "ghost"}
                          size="sm"
                          onClick={() => setCurrentPage(page)}
                          className={page === currentPage
                            ? "bg-emerald-600 hover:bg-emerald-700"
                            : "text-slate-300 hover:bg-slate-800 hover:text-slate-100 min-w-[32px]"}
                        >
                          {page}
                        </Button>
                      ))}
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                        disabled={currentPage === totalPages}
                        className="border-slate-700 text-slate-300 hover:bg-slate-800 hover:text-slate-100"
                      >
                        <ChevronRight className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                )}
              </>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
