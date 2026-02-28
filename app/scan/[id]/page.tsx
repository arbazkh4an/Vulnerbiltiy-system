"use client"

import { useEffect, useState, useRef, useTransition } from "react"
import { useUser } from "@clerk/nextjs"
import { useRouter, useParams } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import {
  Shield,
  ArrowLeft,
  Download,
  Loader2,
  AlertCircle,
  CheckCircle,
  Clock,
  FileText,
  ExternalLink,
  Share2,
  Copy,
  Check,
  ChevronDown,
  ChevronUp,
  ArrowUpDown,
  Filter,
  X,
  Activity,
  Zap,
  Target,
  TrendingUp,
  AlertTriangle,
  ShieldCheck,
  ShieldAlert,
} from "lucide-react"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Progress
} from "@/components/ui/progress"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuCheckboxItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import Link from "next/link"
import type { CVE, Vulnerability, Scan } from "@/lib/types"

type SortOption = "severity" | "cvss" | "name" | "type"
type SortDirection = "asc" | "desc"

function getSeverityColor(severity: string) {
  switch (severity.toLowerCase()) {
    case "critical":
      return "bg-red-500/15 border-red-500/40 text-red-300 shadow-[0_0_20px_rgba(239,68,68,0.15)]"
    case "high":
      return "bg-orange-500/15 border-orange-500/40 text-orange-300 shadow-[0_0_20px_rgba(249,115,22,0.1)]"
    case "medium":
      return "bg-amber-500/15 border-amber-500/40 text-amber-300 shadow-[0_0_15px_rgba(245,158,11,0.1)]"
    case "low":
      return "bg-blue-500/15 border-blue-500/40 text-blue-300 shadow-[0_0_15px_rgba(59,130,246,0.1)]"
    default:
      return "bg-slate-500/15 border-slate-500/40 text-slate-300"
  }
}

function getStatusBadgeColor(status: string) {
  switch (status.toLowerCase()) {
    case "completed":
      return "bg-emerald-500/15 border-emerald-500/40 text-emerald-300 shadow-[0_0_15px_rgba(16,185,129,0.15)]"
    case "running":
      return "bg-blue-500/15 border-blue-500/40 text-blue-300 shadow-[0_0_15px_rgba(59,130,246,0.15)] animate-pulse"
    case "pending":
      return "bg-amber-500/15 border-amber-500/40 text-amber-300 shadow-[0_0_15px_rgba(245,158,11,0.15)]"
    case "failed":
      return "bg-red-500/15 border-red-500/40 text-red-300 shadow-[0_0_15px_rgba(239,68,68,0.15)]"
    default:
      return "bg-slate-500/15 border-slate-500/40 text-slate-300"
  }
}

function getSeverityBadge({ severity }: { severity: string }) {
  return <Badge className={`${getSeverityColor(severity)} border px-3 py-0.5 text-xs font-semibold tracking-wide`}>{severity.toUpperCase()}</Badge>
}

function getStatusBadge({ status }: { status: string }) {
  const statusLabel = status.charAt(0).toUpperCase() + status.slice(1)
  return <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold border ${getStatusBadgeColor(status)}`}>{statusLabel}</span>
}

export default function ScanResultsPage() {
  const { user, isLoaded, isSignedIn } = useUser()
  const router = useRouter()
  const params = useParams()
  const scanId = params.id as string
  const [isPending, startTransition] = useTransition()

  const [scan, setScan] = useState<Scan | null>(null)
  const [vulnerabilities, setVulnerabilities] = useState<Vulnerability[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [downloadingPdf, setDownloadingPdf] = useState(false)
  const [pdfError, setPdfError] = useState<string | null>(null)

  // Sorting and filtering state
  const [sortBy, setSortBy] = useState<SortOption>("severity")
  const [sortDirection, setSortDirection] = useState<SortDirection>("desc")
  const [severityFilter, setSeverityFilter] = useState<string[]>(["critical", "high", "medium", "low"])
  const [typeFilter, setTypeFilter] = useState<string>("all")

  // Share functionality
  const [copied, setCopied] = useState(false)

  // CVE Modal state
  const [selectedCVE, setSelectedCVE] = useState<CVE | null>(null)
  const [cveModalOpen, setCveModalOpen] = useState(false)

  // Evidence expansion state (track by vulnerability id)
  const [expandedEvidence, setExpandedEvidence] = useState<Set<number>>(new Set())

  useEffect(() => {
    if (isLoaded && !isSignedIn) {
      router.push("/")
    }
  }, [isLoaded, isSignedIn, router])

  useEffect(() => {
    const controller = new AbortController()
    
    async function fetchScanResults() {
      setLoading(true)
      setError(null)
      try {
        const response = await fetch(`/api/scans/${scanId}`, { signal: controller.signal })
        if (response.ok) {
          const data = await response.json()
          setScan(data.scan)
          setVulnerabilities(data.vulnerabilities || [])
        } else {
          setError("Failed to load scan results. Please try again.")
          setScan(null)
        }
      } catch (err) {
        if (err instanceof Error && err.name !== "AbortError") {
          setError("An error occurred while loading the scan. Please try again.")
        }
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false)
        }
      }
    }

    if (user && scanId) {
      fetchScanResults()
    }

    return () => {
      controller.abort()
    }
  }, [user, scanId])

  // Polling for scan status updates when scan is running
  useEffect(() => {
    if (!scan || scan.scan_status === "completed" || scan.scan_status === "failed") {
      return
    }

    const pollingIdRef = { current: 0 }
    let isCancelled = false

    const intervalId = setInterval(async () => {
      pollingIdRef.current += 1
      const currentPollingId = pollingIdRef.current

      try {
        const response = await fetch(`/api/scans/${scanId}`)
        if (isCancelled) return
        
        if (response.ok) {
          const data = await response.json()
          // Only update state if this is the most recent polling request
          if (currentPollingId === pollingIdRef.current) {
            setScan(data.scan)
            setVulnerabilities(data.vulnerabilities || [])
          }
        }
      } catch (err) {
        // Silently handle polling errors - will retry
      }
    }, 5000) // Poll every 5 seconds

    return () => {
      isCancelled = true
      clearInterval(intervalId)
    }
  }, [scan?.scan_status, scanId])

async function handleDownloadPdf() {
    setDownloadingPdf(true)
    setPdfError(null)
    try {
      const response = await fetch(`/api/scans/${scanId}/pdf`)
      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement("a")
        a.href = url
        a.download = `vulnerability-report-${scanId}.pdf`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
      } else {
        const errorData = await response.json().catch(() => ({}))
        setPdfError(errorData.error || "Failed to generate PDF report. Please try again.")
      }
    } catch (err) {
      setPdfError("An error occurred while generating the PDF. Please try again.")
    } finally {
      setDownloadingPdf(false)
    }
  }

  async function handleShare() {
    try {
      await navigator.clipboard.writeText(window.location.href)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      setCopied(false)
    }
  }

  function handleCVEClick(cve: CVE) {
    setSelectedCVE(cve)
    setCveModalOpen(true)
  }

  function toggleEvidence(vulnId: number) {
    setExpandedEvidence(prev => {
      const newSet = new Set(prev)
      if (newSet.has(vulnId)) {
        newSet.delete(vulnId)
      } else {
        newSet.add(vulnId)
      }
      return newSet
    })
  }

  function handleSeverityFilterChange(severity: string, checked: boolean) {
    setSeverityFilter(prev => {
      if (checked) {
        return [...prev, severity]
      }
      return prev.filter(s => s !== severity)
    })
  }

  // Filter and sort vulnerabilities
  const filteredAndSortedVulnerabilities = [...vulnerabilities]
    .filter(vuln => severityFilter.includes(vuln.severity.toLowerCase()))
    .filter(vuln => typeFilter === "all" || vuln.vulnerability_type === typeFilter)
    .sort((a, b) => {
      let comparison = 0
      switch (sortBy) {
        case "severity":
          const severityOrder = { critical: 4, high: 3, medium: 2, low: 1 }
          comparison = severityOrder[b.severity.toLowerCase() as keyof typeof severityOrder] - 
                       severityOrder[a.severity.toLowerCase() as keyof typeof severityOrder]
          break
        case "cvss":
          comparison = b.cvss_score - a.cvss_score
          break
        case "name":
          comparison = a.vulnerability_name.localeCompare(b.vulnerability_name)
          break
        case "type":
          comparison = a.vulnerability_type.localeCompare(b.vulnerability_type)
          break
      }
      return sortDirection === "asc" ? -comparison : comparison
    })

  // Get unique vulnerability types for filter
  const vulnerabilityTypes = Array.from(new Set(vulnerabilities.map(v => v.vulnerability_type)))

  // Loading state with retry option
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
        <Loader2 className="h-8 w-8 animate-spin text-emerald-400" />
      </div>
    )
  }

  // Error state with retry option
  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
        <Card className="border-slate-800 bg-slate-900/50">
          <CardContent className="p-8 text-center">
            <AlertCircle className="h-12 w-12 text-red-400 mx-auto mb-4" />
            <p className="text-slate-300 mb-4">{error}</p>
            <div className="flex gap-4 justify-center">
              <Button 
                onClick={() => window.location.reload()} 
                className="bg-emerald-600 hover:bg-emerald-700"
              >
                Retry
              </Button>
              <Link href="/dashboard">
                <Button variant="ghost" className="text-slate-300">
                  Return to Dashboard
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (!scan) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
        <Card className="border-slate-800 bg-slate-900/50">
          <CardContent className="p-8 text-center">
            <AlertCircle className="h-12 w-12 text-slate-400 mx-auto mb-4" />
            <p className="text-slate-300">Scan not found</p>
            <Link href="/dashboard">
              <Button className="mt-4 bg-emerald-600 hover:bg-emerald-700">Return to Dashboard</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      {/* Navigation */}
      <nav className="border-b border-slate-800 bg-slate-900/50 backdrop-blur">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link href="/dashboard" className="flex items-center gap-2">
              <Shield className="h-8 w-8 text-emerald-400" />
              <span className="text-xl font-bold text-slate-100">VulnScan AI</span>
            </Link>
            <Button 
              variant="ghost" 
              className="text-slate-300 hover:text-slate-100"
              onClick={() => {
                startTransition(() => {
                  router.push("/dashboard")
                })
              }}
              disabled={isPending}
            >
              {isPending ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <ArrowLeft className="h-4 w-4 mr-2" />
              )}
              {isPending ? "Navigating..." : "Back to Dashboard"}
            </Button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Summary Section */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-slate-100 mb-4 flex items-center gap-2">
            <ShieldCheck className="h-6 w-6 text-emerald-400" />
            Security Assessment Summary
          </h2>
          <div className="grid md:grid-cols-4 gap-4">
            <Card className="border-slate-700/50 bg-gradient-to-br from-slate-800/80 to-slate-900/80 backdrop-blur">
              <CardContent className="p-5">
                <div className="flex items-center justify-between mb-3">
                  <div className="p-2 rounded-lg bg-emerald-500/10">
                    <FileText className="h-5 w-5 text-emerald-400" />
                  </div>
                  <span className="text-xs text-emerald-400/80 font-medium">Total Issues</span>
                </div>
                <p className="text-3xl font-bold text-slate-100">{scan.total_vulnerabilities}</p>
                <p className="text-xs text-slate-400 mt-1">vulnerabilities detected</p>
              </CardContent>
            </Card>

            <Card className="border-red-500/20 bg-gradient-to-br from-red-950/30 to-slate-900/80 backdrop-blur">
              <CardContent className="p-5">
                <div className="flex items-center justify-between mb-3">
                  <div className="p-2 rounded-lg bg-red-500/10">
                    <ShieldAlert className="h-5 w-5 text-red-400" />
                  </div>
                  <span className="text-xs text-red-400/80 font-medium">Critical Risk</span>
                </div>
                <p className="text-3xl font-bold text-red-400">{scan.critical_count}</p>
                <p className="text-xs text-slate-400 mt-1">critical severity</p>
              </CardContent>
            </Card>

            <Card className="border-orange-500/20 bg-gradient-to-br from-orange-950/30 to-slate-900/80 backdrop-blur">
              <CardContent className="p-5">
                <div className="flex items-center justify-between mb-3">
                  <div className="p-2 rounded-lg bg-orange-500/10">
                    <AlertTriangle className="h-5 w-5 text-orange-400" />
                  </div>
                  <span className="text-xs text-orange-400/80 font-medium">High Risk</span>
                </div>
                <p className="text-3xl font-bold text-orange-400">{scan.high_count}</p>
                <p className="text-xs text-slate-400 mt-1">high severity</p>
              </CardContent>
            </Card>

            <Card className="border-blue-500/20 bg-gradient-to-br from-blue-950/30 to-slate-900/80 backdrop-blur">
              <CardContent className="p-5">
                <div className="flex items-center justify-between mb-3">
                  <div className="p-2 rounded-lg bg-blue-500/10">
                    <Target className="h-5 w-5 text-blue-400" />
                  </div>
                  <span className="text-xs text-blue-400/80 font-medium">Medium/Low</span>
                </div>
                <p className="text-3xl font-bold text-blue-400">{scan.medium_count + scan.low_count}</p>
                <p className="text-xs text-slate-400 mt-1">other findings</p>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Timeline Section */}
        <Card className="border-slate-700/50 bg-slate-900/60 backdrop-blur mb-8">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className={`p-2 rounded-full ${scan.scan_status === 'completed' ? 'bg-emerald-500/20' : scan.scan_status === 'running' ? 'bg-blue-500/20' : 'bg-amber-500/20'}`}>
                  {scan.scan_status === 'completed' ? (
                    <CheckCircle className="h-5 w-5 text-emerald-400" />
                  ) : scan.scan_status === 'running' ? (
                    <Activity className="h-5 w-5 text-blue-400 animate-pulse" />
                  ) : (
                    <Clock className="h-5 w-5 text-amber-400" />
                  )}
                </div>
                <div>
                  <p className="font-semibold text-slate-100 capitalize">{scan.scan_status === 'completed' ? 'Scan Complete' : scan.scan_status === 'running' ? 'Scan In Progress' : 'Scan Pending'}</p>
                  <p className="text-sm text-slate-400">
                    {scan.scan_status === 'completed' 
                      ? `Completed on ${new Date(scan.completed_at || scan.started_at).toLocaleString()}`
                      : scan.scan_status === 'running'
                      ? `Started on ${new Date(scan.started_at).toLocaleString()}`
                      : `Started on ${new Date(scan.started_at).toLocaleString()}`
                    }
                  </p>
                </div>
              </div>
              {getStatusBadge({ status: scan.scan_status })}
            </div>
            
            {/* Progress Timeline */}
            <div className="mt-6 relative">
              <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-slate-700"></div>
              <div className="space-y-6">
                {/* Step 1: Scan Initiated */}
                <div className="flex items-center gap-4 relative">
                  <div className="w-12 h-12 rounded-full bg-emerald-500/20 border-2 border-emerald-500 flex items-center justify-center z-10">
                    <Zap className="h-5 w-5 text-emerald-400" />
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-slate-100">Scan Initiated</p>
                    <p className="text-sm text-slate-400">{new Date(scan.started_at).toLocaleString()}</p>
                  </div>
                  <CheckCircle className="h-5 w-5 text-emerald-400" />
                </div>

                {/* Step 2: Scanning (conditional) */}
                {scan.scan_status === 'running' || scan.scan_status === 'completed' ? (
                  <div className="flex items-center gap-4 relative">
                    <div className={`w-12 h-12 rounded-full ${scan.scan_status === 'completed' ? 'bg-emerald-500/20 border-2 border-emerald-500' : 'bg-blue-500/20 border-2 border-blue-500'} flex items-center justify-center z-10`}>
                      {scan.scan_status === 'completed' ? (
                        <CheckCircle className="h-5 w-5 text-emerald-400" />
                      ) : (
                        <Activity className="h-5 w-5 text-blue-400 animate-pulse" />
                      )}
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-slate-100">Scanning Target</p>
                      <p className="text-sm text-slate-400">
                        {scan.scan_status === 'completed' 
                          ? 'Analysis completed' 
                          : 'Analyzing endpoints and checking for vulnerabilities...'
                        }
                      </p>
                    </div>
                    {scan.scan_status === 'running' && (
                      <Progress value={65} className="w-24 h-2" />
                    )}
                  </div>
                ) : (
                  <div className="flex items-center gap-4 relative">
                    <div className="w-12 h-12 rounded-full bg-slate-800 border-2 border-slate-600 flex items-center justify-center z-10">
                      <Activity className="h-5 w-5 text-slate-500" />
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-slate-500">Scanning Target</p>
                      <p className="text-sm text-slate-500">Pending...</p>
                    </div>
                  </div>
                )}

                {/* Step 3: Completed (conditional) */}
                {scan.scan_status === 'completed' ? (
                  <div className="flex items-center gap-4 relative">
                    <div className="w-12 h-12 rounded-full bg-emerald-500/20 border-2 border-emerald-500 flex items-center justify-center z-10">
                      <ShieldCheck className="h-5 w-5 text-emerald-400" />
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-slate-100">Results Generated</p>
                      <p className="text-sm text-slate-400">
                        Found {scan.total_vulnerabilities} vulnerabilities
                      </p>
                    </div>
                    <CheckCircle className="h-5 w-5 text-emerald-400" />
                  </div>
                ) : scan.scan_status === 'running' ? (
                  <div className="flex items-center gap-4 relative">
                    <div className="w-12 h-12 rounded-full bg-slate-800 border-2 border-slate-600 flex items-center justify-center z-10">
                      <ShieldCheck className="h-5 w-5 text-slate-500" />
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-slate-500">Results Generated</p>
                      <p className="text-sm text-slate-500">Pending...</p>
                    </div>
                  </div>
                ) : null}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Scan Overview */}
        <Card className="border-slate-700/50 bg-slate-900/60 backdrop-blur mb-8">
          <CardHeader>
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <CardTitle className="text-slate-100 mb-2 flex items-center gap-2">
                  Scan Results 
                  {getStatusBadge({ status: scan.scan_status })}
                </CardTitle>
                {/* 
                  Security Note: target_url is rendered via React's default escaping.
                  This field comes from the backend database and is not user-controlled in this view.
                  React automatically escapes content rendered in JSX to prevent XSS attacks.
                */}
                <CardDescription className="text-slate-400 break-all">{scan.target_url}</CardDescription>
                <div className="flex items-center gap-2 mt-3">
                  <Clock className="h-4 w-4 text-slate-500" />
                  <span className="text-sm text-slate-400">
                    Started: {new Date(scan.started_at).toLocaleString()}
                  </span>
                </div>
              </div>
              </div>
              <div className="flex items-center gap-2">
                <Button
                  onClick={handleShare}
                  variant="ghost"
                  className="text-slate-300 hover:text-slate-100"
                >
                  {copied ? (
                    <Check className="h-4 w-4 mr-2 text-emerald-400" />
                  ) : (
                    <Copy className="h-4 w-4 mr-2" />
                  )}
                  {copied ? "Copied!" : "Share"}
                </Button>
                <Button
                  onClick={handleDownloadPdf}
                  className="bg-emerald-600 hover:bg-emerald-700 text-white"
                  disabled={downloadingPdf || scan.scan_status !== "completed"}
                >
                {downloadingPdf ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Download className="h-4 w-4 mr-2" />
                    Download PDF
                  </>
                )}
              </Button>
              {pdfError && (
                <p className="text-sm text-red-400 mt-2">{pdfError}</p>
              )}
            </div>
          </CardHeader>
        </Card>

        {/* Quick Stats - Compact version */}
        <div className="grid md:grid-cols-4 gap-4 mb-8">
          <Card className="border-slate-700/50 bg-slate-800/40">
            <CardContent className="p-4 flex items-center justify-between">
              <div>
                <p className="text-xs text-slate-400 uppercase tracking-wide">Total</p>
                <p className="text-2xl font-bold text-slate-100">{scan.total_vulnerabilities}</p>
              </div>
              <div className="p-2 rounded-lg bg-emerald-500/10">
                <FileText className="h-5 w-5 text-emerald-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="border-red-500/20 bg-red-950/20">
            <CardContent className="p-4 flex items-center justify-between">
              <div>
                <p className="text-xs text-slate-400 uppercase tracking-wide">Critical</p>
                <p className="text-2xl font-bold text-red-400">{scan.critical_count}</p>
              </div>
              <div className="p-2 rounded-lg bg-red-500/10">
                <ShieldAlert className="h-5 w-5 text-red-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="border-orange-500/20 bg-orange-950/20">
            <CardContent className="p-4 flex items-center justify-between">
              <div>
                <p className="text-xs text-slate-400 uppercase tracking-wide">High</p>
                <p className="text-2xl font-bold text-orange-400">{scan.high_count}</p>
              </div>
              <div className="p-2 rounded-lg bg-orange-500/10">
                <AlertTriangle className="h-5 w-5 text-orange-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="border-blue-500/20 bg-blue-950/20">
            <CardContent className="p-4 flex items-center justify-between">
              <div>
                <p className="text-xs text-slate-400 uppercase tracking-wide">Medium/Low</p>
                <p className="text-2xl font-bold text-blue-400">{scan.medium_count + scan.low_count}</p>
              </div>
              <div className="p-2 rounded-lg bg-blue-500/10">
                <Target className="h-5 w-5 text-blue-400" />
              </div>
            </CardContent>
          </Card>
        </div>

{/* Vulnerabilities Table */}
        <Card className="border-slate-800 bg-slate-900/50 backdrop-blur">
          <CardHeader>
            <div className="flex items-start justify-between">
              <div>
                <CardTitle className="text-slate-100">Detected Vulnerabilities</CardTitle>
                <CardDescription className="text-slate-400">
                  Comprehensive list of security issues found during the scan
                </CardDescription>
              </div>
              {vulnerabilities.length > 0 && (
                <div className="flex items-center gap-2 flex-wrap">
                  {/* Sort Dropdown */}
                  <Select
                    value={`${sortBy}-${sortDirection}`}
                    onValueChange={(value) => {
                      const [sort, direction] = value.split("-") as [SortOption, SortDirection]
                      setSortBy(sort)
                      setSortDirection(direction)
                    }}
                  >
                    <SelectTrigger className="w-[160px] bg-slate-800 border-slate-700 text-slate-300">
                      <ArrowUpDown className="h-4 w-4 mr-2" />
                      <SelectValue placeholder="Sort by" />
                    </SelectTrigger>
                    <SelectContent className="bg-slate-800 border-slate-700">
                      <SelectItem value="severity-desc">Severity (High-Low)</SelectItem>
                      <SelectItem value="severity-asc">Severity (Low-High)</SelectItem>
                      <SelectItem value="cvss-desc">CVSS (High-Low)</SelectItem>
                      <SelectItem value="cvss-asc">CVSS (Low-High)</SelectItem>
                      <SelectItem value="name-asc">Name (A-Z)</SelectItem>
                      <SelectItem value="name-desc">Name (Z-A)</SelectItem>
                      <SelectItem value="type-asc">Type (A-Z)</SelectItem>
                      <SelectItem value="type-desc">Type (Z-A)</SelectItem>
                    </SelectContent>
                  </Select>

                  {/* Type Filter */}
                  <Select value={typeFilter} onValueChange={setTypeFilter}>
                    <SelectTrigger className="w-[180px] bg-slate-800 border-slate-700 text-slate-300">
                      <Filter className="h-4 w-4 mr-2" />
                      <SelectValue placeholder="Filter by type" />
                    </SelectTrigger>
                    <SelectContent className="bg-slate-800 border-slate-700">
                      <SelectItem value="all">All Types</SelectItem>
                      {vulnerabilityTypes.map(type => (
                        <SelectItem key={type} value={type}>{type}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>

                  {/* Severity Filter */}
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="outline" className="bg-slate-800 border-slate-700 text-slate-300">
                        <Filter className="h-4 w-4 mr-2" />
                        Severity
                        {severityFilter.length < 4 && (
                          <Badge variant="secondary" className="ml-2 bg-emerald-600">
                            {severityFilter.length}
                          </Badge>
                        )}
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent className="bg-slate-800 border-slate-700">
                      <DropdownMenuLabel className="text-slate-300">Filter by Severity</DropdownMenuLabel>
                      <DropdownMenuSeparator className="bg-slate-700" />
                      <DropdownMenuCheckboxItem
                        checked={severityFilter.includes("critical")}
                        onCheckedChange={(checked) => handleSeverityFilterChange("critical", checked)}
                        className="text-slate-300 focus:bg-slate-700 focus:text-slate-100"
                      >
                        Critical
                      </DropdownMenuCheckboxItem>
                      <DropdownMenuCheckboxItem
                        checked={severityFilter.includes("high")}
                        onCheckedChange={(checked) => handleSeverityFilterChange("high", checked)}
                        className="text-slate-300 focus:bg-slate-700 focus:text-slate-100"
                      >
                        High
                      </DropdownMenuCheckboxItem>
                      <DropdownMenuCheckboxItem
                        checked={severityFilter.includes("medium")}
                        onCheckedChange={(checked) => handleSeverityFilterChange("medium", checked)}
                        className="text-slate-300 focus:bg-slate-700 focus:text-slate-100"
                      >
                        Medium
                      </DropdownMenuCheckboxItem>
                      <DropdownMenuCheckboxItem
                        checked={severityFilter.includes("low")}
                        onCheckedChange={(checked) => handleSeverityFilterChange("low", checked)}
                        className="text-slate-300 focus:bg-slate-700 focus:text-slate-100"
                      >
                        Low
                      </DropdownMenuCheckboxItem>
                    </DropdownMenuContent>
                  </DropdownMenu>

                  {/* Clear Filters */}
                  {(severityFilter.length < 4 || typeFilter !== "all") && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        setSeverityFilter(["critical", "high", "medium", "low"])
                        setTypeFilter("all")
                      }}
                      className="text-slate-400 hover:text-slate-200"
                    >
                      <X className="h-4 w-4 mr-1" />
                      Clear
                    </Button>
                  )}
                </div>
              )}
            </div>
          </CardHeader>
<CardContent>
            {vulnerabilities.length === 0 ? (
              <div className="text-center py-12">
                <CheckCircle className="h-12 w-12 text-emerald-400 mx-auto mb-4" />
                <p className="text-slate-300 font-medium mb-2">No vulnerabilities found!</p>
                <p className="text-slate-400 text-sm">This target appears to be secure.</p>
              </div>
            ) : filteredAndSortedVulnerabilities.length === 0 ? (
              <div className="text-center py-12">
                <AlertCircle className="h-12 w-12 text-slate-400 mx-auto mb-4" />
                <p className="text-slate-300 font-medium mb-2">No matching vulnerabilities</p>
                <p className="text-slate-400 text-sm mb-4">Try adjusting your filters</p>
                <Button
                  variant="outline"
                  onClick={() => {
                    setSeverityFilter(["critical", "high", "medium", "low"])
                    setTypeFilter("all")
                  }}
                  className="border-slate-600 text-slate-300 hover:bg-slate-800"
                >
                  Clear Filters
                </Button>
              </div>
            ) : (
              <>
                <p className="text-sm text-slate-400 mb-4">
                  Showing {filteredAndSortedVulnerabilities.length} of {vulnerabilities.length} vulnerabilities
                </p>
                <div className="space-y-4">
                  {filteredAndSortedVulnerabilities.map((vuln) => (
                  <div 
                    key={vuln.id} 
                    className={`p-5 bg-slate-800/40 border rounded-xl space-y-4 transition-all duration-200 hover:bg-slate-800/60 hover:shadow-lg hover:shadow-slate-900/50 ${
                      vuln.severity === 'critical' 
                        ? 'border-red-500/30 hover:border-red-500/50' 
                        : vuln.severity === 'high'
                        ? 'border-orange-500/30 hover:border-orange-500/50'
                        : vuln.severity === 'medium'
                        ? 'border-amber-500/30 hover:border-amber-500/50'
                        : 'border-blue-500/30 hover:border-blue-500/50'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-3">
                          <h3 className="text-lg font-bold text-slate-100">{vuln.vulnerability_name}</h3>
                          {getSeverityBadge({ severity: vuln.severity })}
                        </div>
                        <div className="flex items-center gap-2 mb-3">
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                            {vuln.vulnerability_type}
                          </span>
                        </div>
                        <p className="text-slate-300 leading-relaxed">{vuln.description}</p>
                      </div>
                      <div className="hidden md:flex flex-col items-center justify-center ml-4 p-3 bg-slate-900/60 rounded-lg border border-slate-700/50">
                        <span className="text-xs text-slate-400 uppercase tracking-wider mb-1">CVSS</span>
                        <span className={`text-2xl font-bold ${
                          vuln.cvss_score >= 9 ? 'text-red-400' :
                          vuln.cvss_score >= 7 ? 'text-orange-400' :
                          vuln.cvss_score >= 4 ? 'text-amber-400' :
                          'text-blue-400'
                        }`}>{vuln.cvss_score}</span>
                        <span className="text-xs text-slate-500">/ 10</span>
                      </div>
                    </div>

                    <div className="grid md:grid-cols-2 gap-4 pt-2 border-t border-slate-700/50">
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-xs font-medium text-slate-400 mb-1">CWE Classification</p>
                            <div className="flex items-center gap-2">
                              <Badge variant="outline" className="border-slate-600 text-slate-300 bg-slate-800/50">
                                {vuln.cwe_id}
                              </Badge>
                              <span className="text-sm text-slate-400">{vuln.cwe_name}</span>
                            </div>
                          </div>
                          <div className="text-right">
                            <p className="text-xs font-medium text-slate-400 mb-1">AI Confidence</p>
                            <span className="text-sm font-semibold text-emerald-400">{vuln.ai_confidence.toFixed(0)}%</span>
                          </div>
                        </div>

                        <div>
                          <p className="text-xs font-medium text-slate-400 mb-1">AI Prediction</p>
                          <div className="flex items-center gap-2">
                            {getSeverityBadge({ severity: vuln.ai_predicted_severity })}
                          </div>
                        </div>

                        {vuln.cves && vuln.cves.length > 0 && (
                          <div>
                            <p className="text-xs font-medium text-slate-400 mb-1">Associated CVEs</p>
                            <div className="flex flex-wrap gap-2">
                              {vuln.cves.map((cve) => (
                                <button
                                  key={cve.cve_id}
                                  onClick={() => handleCVEClick(cve)}
                                  className="inline-flex items-center gap-1 px-2 py-1 bg-slate-700/50 border border-slate-600 rounded text-xs text-slate-300 hover:border-emerald-500/50 hover:text-emerald-400 transition-colors cursor-pointer"
                                >
                                  {cve.cve_id}
                                  <ExternalLink className="h-3 w-3" />
                                </button>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>

                      <div className="space-y-3">
                        <div>
                          <p className="text-xs font-medium text-slate-400 mb-1">Affected Location</p>
                          {/* 
                            Security Note: affected_url is rendered via React's default escaping.
                            This URL is extracted from scan results and represents the vulnerable endpoint.
                            React automatically escapes content rendered in JSX to prevent XSS attacks.
                            The URL is displayed in a monospace font for readability but not executed.
                          */}
                          <p className="text-sm text-slate-300 break-all font-mono bg-slate-900/50 p-2 rounded border border-slate-700/50">
                            {vuln.affected_url}
                          </p>
                        </div>

                        <Collapsible
                          open={expandedEvidence.has(vuln.id)}
                          onOpenChange={() => toggleEvidence(vuln.id)}
                        >
                          <CollapsibleTrigger asChild>
                            <button className="flex items-center gap-2 text-xs font-medium text-slate-400 hover:text-slate-300 transition-colors w-full">
                              {expandedEvidence.has(vuln.id) ? (
                                <ChevronUp className="h-4 w-4" />
                              ) : (
                                <ChevronDown className="h-4 w-4" />
                              )}
                              Evidence
                            </button>
                          </CollapsibleTrigger>
                          <CollapsibleContent className="mt-2">
                            {/* 
                              Security Note: evidence is rendered via React's default escaping.
                              This field contains scan evidence/output from vulnerability detection.
                              React automatically escapes content rendered in JSX to prevent XSS attacks.
                              The evidence is displayed in a monospace font for readability but not executed.
                            */}
                            <p className="text-sm text-slate-300 font-mono bg-slate-900/50 p-2 rounded border border-slate-700/50 break-all">
                              {vuln.evidence}
                            </p>
                          </CollapsibleContent>
                        </Collapsible>

                        <Collapsible
                          open={expandedEvidence.has(vuln.id + 100000)}
                          onOpenChange={() => toggleEvidence(vuln.id + 100000)}
                        >
                          <CollapsibleTrigger asChild>
                            <button className="flex items-center gap-2 text-xs font-medium text-slate-400 hover:text-slate-300 transition-colors w-full">
                              {expandedEvidence.has(vuln.id + 100000) ? (
                                <ChevronUp className="h-4 w-4" />
                              ) : (
                                <ChevronDown className="h-4 w-4" />
                              )}
                              Remediation
                            </button>
                          </CollapsibleTrigger>
                          <CollapsibleContent className="mt-2">
                            <p className="text-sm text-slate-300 bg-emerald-500/10 border border-emerald-500/30 p-3 rounded">
                              {vuln.remediation}
                            </p>
                          </CollapsibleContent>
                        </Collapsible>
                      </div>
                    </div>
                  </div>
                ))}
                </div>
              </>
            )}
          </CardContent>
        </Card>

        {/* CVE Details Modal */}
        <Dialog open={cveModalOpen} onOpenChange={setCveModalOpen}>
          <DialogContent className="bg-slate-900 border-slate-700 text-slate-100 max-w-2xl">
            <DialogHeader>
              <DialogTitle className="text-slate-100 flex items-center gap-2">
                <Shield className="h-5 w-5 text-emerald-400" />
                {selectedCVE?.cve_id}
              </DialogTitle>
              <DialogDescription className="text-slate-400">
                CVE Details
              </DialogDescription>
            </DialogHeader>
            {selectedCVE && (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 bg-slate-800/50 rounded-lg">
                    <p className="text-xs text-slate-400 mb-1">CVSS v3 Score</p>
                    <p className="text-2xl font-bold text-slate-100">{selectedCVE.cvss_v3_score}</p>
                  </div>
                  <div className="p-4 bg-slate-800/50 rounded-lg">
                    <p className="text-xs text-slate-400 mb-1">Published Date</p>
                    <p className="text-sm text-slate-100">
                      {new Date(selectedCVE.published_date).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                <div className="p-4 bg-slate-800/50 rounded-lg">
                  <p className="text-xs text-slate-400 mb-2">Description</p>
                  <p className="text-sm text-slate-300">{selectedCVE.cve_description}</p>
                </div>
                <div className="flex gap-2">
                  <a
                    href={`https://nvd.nist.gov/vuln/detail/${selectedCVE.cve_id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex-1"
                  >
                    <Button className="w-full bg-emerald-600 hover:bg-emerald-700">
                      <ExternalLink className="h-4 w-4 mr-2" />
                      View on NVD
                    </Button>
                  </a>
                  <Button
                    variant="outline"
                    onClick={() => setCveModalOpen(false)}
                    className="border-slate-600 text-slate-300 hover:bg-slate-800"
                  >
                    Close
                  </Button>
                </div>
              </div>
            )}
          </DialogContent>
        </Dialog>
      </div>
    </div>
  )
}
