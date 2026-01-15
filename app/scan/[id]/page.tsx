"use client"

import { useEffect, useState } from "react"
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
} from "lucide-react"
import Link from "next/link"

interface CVE {
  cve_id: string
  cve_description: string
  cvss_v3_score: number
  published_date: string
}

interface Vulnerability {
  id: number
  vulnerability_name: string
  vulnerability_type: string
  description: string
  cwe_id: string
  cwe_name: string
  cvss_score: number
  severity: string
  ai_predicted_severity: string
  ai_confidence: number
  remediation: string
  affected_url: string
  evidence: string
  cves: CVE[]
}

interface Scan {
  id: number
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

export default function ScanResultsPage() {
  const { user, isLoaded, isSignedIn } = useUser()
  const router = useRouter()
  const params = useParams()
  const scanId = params.id as string

  const [scan, setScan] = useState<Scan | null>(null)
  const [vulnerabilities, setVulnerabilities] = useState<Vulnerability[]>([])
  const [loading, setLoading] = useState(true)
  const [downloadingPdf, setDownloadingPdf] = useState(false)

  useEffect(() => {
    if (isLoaded && !isSignedIn) {
      router.push("/")
    }
  }, [isLoaded, isSignedIn, router])

  useEffect(() => {
    if (user && scanId) {
      fetchScanResults()
    }
  }, [user, scanId])

  async function fetchScanResults() {
    try {
      const response = await fetch(`/api/scans/${scanId}`)
      if (response.ok) {
        const data = await response.json()
        setScan(data.scan)
        setVulnerabilities(data.vulnerabilities || [])
      } else {
        console.error("[v0] Failed to fetch scan results")
      }
    } catch (err) {
      console.error("[v0] Error fetching scan results:", err)
    } finally {
      setLoading(false)
    }
  }

  async function handleDownloadPdf() {
    setDownloadingPdf(true)
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
      }
    } catch (err) {
      console.error("[v0] Error downloading PDF:", err)
    } finally {
      setDownloadingPdf(false)
    }
  }

  function getSeverityColor(severity: string) {
    switch (severity.toLowerCase()) {
      case "critical":
        return "bg-red-500/10 border-red-500/50 text-red-400"
      case "high":
        return "bg-orange-500/10 border-orange-500/50 text-orange-400"
      case "medium":
        return "bg-yellow-500/10 border-yellow-500/50 text-yellow-400"
      case "low":
        return "bg-blue-500/10 border-blue-500/50 text-blue-400"
      default:
        return "bg-slate-500/10 border-slate-500/50 text-slate-400"
    }
  }

  function getSeverityBadge(severity: string) {
    return <Badge className={getSeverityColor(severity)}>{severity.toUpperCase()}</Badge>
  }

  if (!isLoaded || loading || !user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
        <Loader2 className="h-8 w-8 animate-spin text-emerald-400" />
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
            <Link href="/dashboard">
              <Button variant="ghost" className="text-slate-300 hover:text-slate-100">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Dashboard
              </Button>
            </Link>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Scan Overview */}
        <Card className="border-slate-800 bg-slate-900/50 backdrop-blur mb-8">
          <CardHeader>
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <CardTitle className="text-slate-100 mb-2">Scan Results</CardTitle>
                <CardDescription className="text-slate-400 break-all">{scan.target_url}</CardDescription>
                <div className="flex items-center gap-2 mt-2">
                  {scan.scan_status === "completed" && <CheckCircle className="h-4 w-4 text-emerald-400" />}
                  {scan.scan_status === "running" && <Clock className="h-4 w-4 text-blue-400 animate-pulse" />}
                  <span className="text-sm text-slate-400">
                    {scan.scan_status === "completed" ? "Completed" : "In Progress"} •{" "}
                    {new Date(scan.started_at).toLocaleString()}
                  </span>
                </div>
              </div>
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
            </div>
          </CardHeader>
        </Card>

        {/* Stats Cards */}
        <div className="grid md:grid-cols-4 gap-4 mb-8">
          <Card className="border-slate-800 bg-slate-900/50">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-400">Total Vulnerabilities</p>
                  <p className="text-3xl font-bold text-slate-100">{scan.total_vulnerabilities}</p>
                </div>
                <FileText className="h-8 w-8 text-emerald-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="border-red-500/20 bg-red-500/5">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-400">Critical</p>
                  <p className="text-3xl font-bold text-red-400">{scan.critical_count}</p>
                </div>
                <AlertCircle className="h-8 w-8 text-red-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="border-orange-500/20 bg-orange-500/5">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-400">High</p>
                  <p className="text-3xl font-bold text-orange-400">{scan.high_count}</p>
                </div>
                <AlertCircle className="h-8 w-8 text-orange-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="border-yellow-500/20 bg-yellow-500/5">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-400">Medium / Low</p>
                  <p className="text-3xl font-bold text-yellow-400">{scan.medium_count + scan.low_count}</p>
                </div>
                <AlertCircle className="h-8 w-8 text-yellow-400" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Vulnerabilities Table */}
        <Card className="border-slate-800 bg-slate-900/50 backdrop-blur">
          <CardHeader>
            <CardTitle className="text-slate-100">Detected Vulnerabilities</CardTitle>
            <CardDescription className="text-slate-400">
              Comprehensive list of security issues found during the scan
            </CardDescription>
          </CardHeader>
          <CardContent>
            {vulnerabilities.length === 0 ? (
              <div className="text-center py-12">
                <CheckCircle className="h-12 w-12 text-emerald-400 mx-auto mb-4" />
                <p className="text-slate-300 font-medium mb-2">No vulnerabilities found!</p>
                <p className="text-slate-400 text-sm">This target appears to be secure.</p>
              </div>
            ) : (
              <div className="space-y-6">
                {vulnerabilities.map((vuln) => (
                  <div key={vuln.id} className="p-4 bg-slate-800/50 border border-slate-700 rounded-lg space-y-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="text-lg font-semibold text-slate-100">{vuln.vulnerability_name}</h3>
                          {getSeverityBadge(vuln.severity)}
                        </div>
                        <p className="text-sm text-emerald-400 mb-2">{vuln.vulnerability_type}</p>
                        <p className="text-slate-300 mb-3">{vuln.description}</p>
                      </div>
                    </div>

                    <div className="grid md:grid-cols-2 gap-4">
                      <div className="space-y-3">
                        <div>
                          <p className="text-xs font-medium text-slate-400 mb-1">CWE Classification</p>
                          <div className="flex items-center gap-2">
                            <Badge variant="outline" className="border-slate-600 text-slate-300">
                              {vuln.cwe_id}
                            </Badge>
                            <span className="text-sm text-slate-400">{vuln.cwe_name}</span>
                          </div>
                        </div>

                        <div>
                          <p className="text-xs font-medium text-slate-400 mb-1">CVSS Score</p>
                          <div className="flex items-center gap-2">
                            <span className="text-lg font-bold text-slate-100">{vuln.cvss_score}</span>
                            <span className="text-sm text-slate-400">/ 10.0</span>
                          </div>
                        </div>

                        <div>
                          <p className="text-xs font-medium text-slate-400 mb-1">AI Prediction</p>
                          <div className="flex items-center gap-2">
                            {getSeverityBadge(vuln.ai_predicted_severity)}
                            <span className="text-sm text-slate-400">{vuln.ai_confidence.toFixed(1)}% confidence</span>
                          </div>
                        </div>

                        {vuln.cves && vuln.cves.length > 0 && (
                          <div>
                            <p className="text-xs font-medium text-slate-400 mb-1">Associated CVEs</p>
                            <div className="flex flex-wrap gap-2">
                              {vuln.cves.map((cve) => (
                                <a
                                  key={cve.cve_id}
                                  href={`https://nvd.nist.gov/vuln/detail/${cve.cve_id}`}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="inline-flex items-center gap-1 px-2 py-1 bg-slate-700/50 border border-slate-600 rounded text-xs text-slate-300 hover:border-emerald-500/50 transition-colors"
                                >
                                  {cve.cve_id}
                                  <ExternalLink className="h-3 w-3" />
                                </a>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>

                      <div className="space-y-3">
                        <div>
                          <p className="text-xs font-medium text-slate-400 mb-1">Affected Location</p>
                          <p className="text-sm text-slate-300 break-all font-mono bg-slate-900/50 p-2 rounded">
                            {vuln.affected_url}
                          </p>
                        </div>

                        <div>
                          <p className="text-xs font-medium text-slate-400 mb-1">Evidence</p>
                          <p className="text-sm text-slate-300 font-mono bg-slate-900/50 p-2 rounded break-all">
                            {vuln.evidence}
                          </p>
                        </div>

                        <div>
                          <p className="text-xs font-medium text-slate-400 mb-1">Remediation</p>
                          <p className="text-sm text-slate-300 bg-emerald-500/10 border border-emerald-500/30 p-3 rounded">
                            {vuln.remediation}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
