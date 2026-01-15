"use client"

import type React from "react"

import { useEffect, useState } from "react"
import { useUser, useClerk } from "@clerk/nextjs"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Alert, AlertDescription } from "@/components/ui/alert"
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
} from "lucide-react"
import Link from "next/link"

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

export default function DashboardPage() {
  const { user, isLoaded, isSignedIn } = useUser()
  const { signOut } = useClerk()
  const router = useRouter()
  const [targetUrl, setTargetUrl] = useState("")
  const [scanning, setScanning] = useState(false)
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")
  const [scans, setScans] = useState<Scan[]>([])
  const [loadingScans, setLoadingScans] = useState(true)

  useEffect(() => {
    if (isLoaded && !isSignedIn) {
      router.push("/")
    }
  }, [isLoaded, isSignedIn, router])

  useEffect(() => {
    if (isSignedIn && user) {
      fetchScans()
    }
  }, [isSignedIn, user])

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
    setScanning(true)

    try {
      // Validate URL
      try {
        new URL(targetUrl)
      } catch {
        throw new Error("Please enter a valid URL")
      }

      const response = await fetch("/api/scans/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: targetUrl }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || "Failed to start scan")
      }

      setSuccess("Scan started successfully!")
      setTargetUrl("")
      fetchScans()

      // Navigate to results page after a short delay
      setTimeout(() => {
        router.push(`/scan/${data.scanId}`)
      }, 1500)
    } catch (err) {
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
            <div className="flex items-center gap-4">
              <span className="text-sm text-slate-400">Welcome, {user.fullName || user.primaryEmailAddress?.emailAddress}</span>
              <Button variant="ghost" size="sm" onClick={() => signOut()} className="text-slate-300 hover:text-slate-100">
                <LogOut className="h-4 w-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Scan Input Section */}
        <Card className="border-slate-800 bg-slate-900/50 backdrop-blur mb-8">
          <CardHeader>
            <CardTitle className="text-slate-100 flex items-center gap-2">
              <Scan className="h-5 w-5 text-emerald-400" />
              Start New Vulnerability Scan
            </CardTitle>
            <CardDescription className="text-slate-400">
              Enter a target URL to scan for OWASP Top 10:2025 vulnerabilities
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleStartScan} className="space-y-4">
              {error && (
                <Alert variant="destructive" className="bg-red-500/10 border-red-500/50">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              {success && (
                <Alert className="bg-emerald-500/10 border-emerald-500/50">
                  <CheckCircle className="h-4 w-4 text-emerald-400" />
                  <AlertDescription className="text-emerald-400">{success}</AlertDescription>
                </Alert>
              )}

              <div className="flex gap-4">
                <Input
                  type="url"
                  placeholder="https://example.com"
                  value={targetUrl}
                  onChange={(e) => setTargetUrl(e.target.value)}
                  required
                  className="flex-1 bg-slate-800/50 border-slate-700 text-slate-100 placeholder:text-slate-500"
                  disabled={scanning}
                />
                <Button type="submit" className="bg-emerald-600 hover:bg-emerald-700 text-white" disabled={scanning}>
                  {scanning ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Scanning...
                    </>
                  ) : (
                    <>
                      <Scan className="h-4 w-4 mr-2" />
                      Start Scan
                    </>
                  )}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>

        {/* Stats Overview */}
        <div className="grid md:grid-cols-4 gap-4 mb-8">
          <Card className="border-slate-800 bg-slate-900/50">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-400">Total Scans</p>
                  <p className="text-2xl font-bold text-slate-100">{scans.length}</p>
                </div>
                <TrendingUp className="h-8 w-8 text-emerald-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="border-slate-800 bg-slate-900/50">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-400">Critical Found</p>
                  <p className="text-2xl font-bold text-red-400">
                    {scans.reduce((sum, scan) => sum + scan.critical_count, 0)}
                  </p>
                </div>
                <AlertCircle className="h-8 w-8 text-red-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="border-slate-800 bg-slate-900/50">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-400">High Priority</p>
                  <p className="text-2xl font-bold text-orange-400">
                    {scans.reduce((sum, scan) => sum + scan.high_count, 0)}
                  </p>
                </div>
                <AlertCircle className="h-8 w-8 text-orange-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="border-slate-800 bg-slate-900/50">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-400">Total Vulnerabilities</p>
                  <p className="text-2xl font-bold text-slate-100">
                    {scans.reduce((sum, scan) => sum + scan.total_vulnerabilities, 0)}
                  </p>
                </div>
                <Shield className="h-8 w-8 text-emerald-400" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Recent Scans */}
        <Card className="border-slate-800 bg-slate-900/50 backdrop-blur">
          <CardHeader>
            <CardTitle className="text-slate-100">Recent Scans</CardTitle>
            <CardDescription className="text-slate-400">View your scan history and results</CardDescription>
          </CardHeader>
          <CardContent>
            {loadingScans ? (
              <div className="flex justify-center py-8">
                <Loader2 className="h-8 w-8 animate-spin text-emerald-400" />
              </div>
            ) : scans.length === 0 ? (
              <div className="text-center py-8">
                <Scan className="h-12 w-12 text-slate-700 mx-auto mb-4" />
                <p className="text-slate-400">No scans yet. Start your first vulnerability scan above!</p>
              </div>
            ) : (
              <div className="space-y-4">
                {scans.map((scan) => (
                  <Link
                    key={scan.id}
                    href={`/scan/${scan.id}`}
                    className="block p-4 bg-slate-800/50 border border-slate-700 rounded-lg hover:border-emerald-500/50 transition-colors"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          {getStatusIcon(scan.scan_status)}
                          <span className="text-sm text-slate-400">{getStatusText(scan.scan_status)}</span>
                        </div>
                        <p className="text-slate-100 font-medium mb-2 break-all">{scan.target_url}</p>
                        <p className="text-sm text-slate-400">{new Date(scan.started_at).toLocaleString()}</p>
                      </div>
                      <div className="flex gap-2 ml-4">
                        {scan.critical_count > 0 && (
                          <span className="px-2 py-1 bg-red-500/10 border border-red-500/50 rounded text-xs text-red-400">
                            {scan.critical_count} Critical
                          </span>
                        )}
                        {scan.high_count > 0 && (
                          <span className="px-2 py-1 bg-orange-500/10 border border-orange-500/50 rounded text-xs text-orange-400">
                            {scan.high_count} High
                          </span>
                        )}
                        {scan.medium_count > 0 && (
                          <span className="px-2 py-1 bg-yellow-500/10 border border-yellow-500/50 rounded text-xs text-yellow-400">
                            {scan.medium_count} Medium
                          </span>
                        )}
                        {scan.low_count > 0 && (
                          <span className="px-2 py-1 bg-blue-500/10 border border-blue-500/50 rounded text-xs text-blue-400">
                            {scan.low_count} Low
                          </span>
                        )}
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
