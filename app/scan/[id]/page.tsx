"use client"

import { useEffect, useState, useTransition } from "react"
import { useRouter, useParams } from "next/navigation"
import { AlertTriangle, CheckCircle, Shield, ArrowLeft, Loader2, PlaySquare } from "lucide-react"
import Link from "next/link"
import type { Vulnerability, Scan } from "@/lib/types"

const MOCK_USER = { fullName: "Local User" }

export default function HackerScanDashboard() {
  const router = useRouter()
  const params = useParams()
  const scanId = params.id as string
  const [isPending, startTransition] = useTransition()

  const [scan, setScan] = useState<Scan | null>(null)
  const [vulnerabilities, setVulnerabilities] = useState<Vulnerability[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

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
        }
      } catch (err) {
        if (err instanceof Error && err.name !== "AbortError") {
          setError("An error occurred while loading the scan.")
        }
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false)
        }
      }
    }

    if (scanId) {
      fetchScanResults()
    }

    return () => {
      controller.abort()
    }
  }, [scanId])

  // Polling for scan status updates when scan is running
  useEffect(() => {
    if (!scan || scan.scan_status === "completed" || scan.scan_status === "failed") {
      return
    }

    let isCancelled = false

    const intervalId = setInterval(async () => {
      try {
        const response = await fetch(`/api/scans/${scanId}`)
        if (isCancelled) return

        if (response.ok) {
          const data = await response.json()
          setScan(data.scan)
          setVulnerabilities(data.vulnerabilities || [])
        }
      } catch (err) {
        // Silently handle polling errors - will retry
      }
    }, 3000)

    return () => {
      isCancelled = true
      clearInterval(intervalId)
    }
  }, [scan?.scan_status, scanId])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#0a0a0c] text-slate-400">
        <Loader2 className="h-8 w-8 animate-spin text-purple-500" />
      </div>
    )
  }

  if (error || !scan) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-[#0a0a0c] text-slate-400">
        <AlertTriangle className="h-12 w-12 text-red-500 mb-4" />
        <p>{error || "Scan not found"}</p>
        <Button className="mt-4" onClick={() => router.push("/dashboard")}>Back to Dashboard</Button>
      </div>
    )
  }

  const isRunning = scan.scan_status !== "completed" && scan.scan_status !== "failed"

  return (
    <div className="min-h-screen bg-[#050505] p-4 md:p-8 font-sans text-slate-300 selection:bg-purple-500/30 flex justify-center items-center">

      {/* Container simulating an application window */}
      <div className="w-full max-w-6xl bg-[#0d0d12] border border-slate-800/60 rounded-xl overflow-hidden shadow-2xl shadow-purple-900/10 flex flex-col h-[85vh]">

        {/* Window Header */}
        <div className="h-10 bg-[#15151b] border-b border-slate-800/80 flex items-center px-4 shrink-0">
          <div className="flex gap-2 w-1/3">
            <div className="w-3 h-3 rounded-full bg-red-500/80"></div>
            <div className="w-3 h-3 rounded-full bg-yellow-500/80"></div>
            <div className="w-3 h-3 rounded-full bg-green-500/80"></div>
          </div>
          <div className="w-1/3 text-center">
            <span className="text-xs text-slate-400 font-mono">vulnscan-dashboard.exe</span>
          </div>
          <div className="w-1/3 flex justify-end">
            <button
              onClick={() => router.push('/dashboard')}
              className="text-xs text-slate-500 hover:text-slate-300 transition-colors flex items-center gap-1"
            >
              <ArrowLeft className="h-3 w-3" /> Dashboard
            </button>
          </div>
        </div>

        {/* Window Body */}
        <div className="flex flex-1 overflow-hidden">

          {/* Sidebar */}
          <div className="w-64 bg-[#111116] border-r border-slate-800/50 p-6 flex flex-col gap-8 shrink-0 overflow-y-auto">

            {/* Targets */}
            <div>
              <h3 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-4">Targets</h3>
              <div className="space-y-3">
                <div className="flex items-center gap-3 text-slate-200">
                  <Shield className="h-4 w-4 text-slate-400" />
                  <span className="text-sm truncate" title={scan.target_url}>
                    {scan.target_url.replace(/^https?:\/\//, '').split('/')[0]}
                  </span>
                </div>
                {/* Mock inactive target for aesthetic */}
                <div className="flex items-center gap-3 text-slate-500">
                  <Shield className="h-4 w-4 opacity-50" />
                  <span className="text-sm">staging-server</span>
                </div>
              </div>
            </div>

            {/* Engines */}
            <div>
              <h3 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-4">Engines</h3>
              <div className="space-y-3 font-mono text-sm text-slate-400">
                <div className="flex items-center gap-2">
                  <span className="text-slate-600">{">_"}</span> SQL Injection
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-slate-600">{">_"}</span> XSS Scanner
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-slate-600">{">_"}</span> CSRF Detection
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-slate-600">{">_"}</span> Auth Bypass
                </div>
              </div>
            </div>

          </div>

          {/* Main Content Area */}
          <div className="flex-1 flex flex-col min-w-0 bg-[#0a0a0e] relative">

            <div className="flex-1 overflow-y-auto p-8">
              {/* Header */}
              <div className="flex items-center justify-between mb-8">
                <h1 className="text-2xl font-bold text-slate-100 tracking-tight">Live Scan Results</h1>

                <div className="flex items-center gap-2">
                  {isRunning ? (
                    <>
                      <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
                      <span className="text-[10px] uppercase font-bold text-emerald-500 tracking-widest">Scanning Active</span>
                    </>
                  ) : (
                    <>
                      <div className="w-2 h-2 rounded-full bg-slate-500"></div>
                      <span className="text-[10px] uppercase font-bold text-slate-500 tracking-widest">Scan Completed</span>
                    </>
                  )}
                </div>
              </div>

              {/* Cards List */}
              <div className="space-y-3">
                {vulnerabilities.length === 0 && !isRunning ? (
                  <div className="flex flex-col items-center justify-center py-16 text-slate-500 border border-slate-800/50 rounded-lg bg-slate-900/20 border-dashed">
                    <CheckCircle className="h-10 w-10 text-emerald-500/50 mb-4" />
                    <p>No vulnerabilities detected.</p>
                  </div>
                ) : vulnerabilities.length === 0 && isRunning ? (
                  <div className="flex flex-col items-center justify-center py-24 text-slate-500">
                    <Loader2 className="h-8 w-8 animate-spin text-purple-500/50 mb-4" />
                    <p className="font-mono text-sm">Awaiting findings...</p>
                  </div>
                ) : (
                  vulnerabilities.map((vuln, i) => (
                    <div key={vuln.id} className="flex items-center justify-between p-4 rounded-xl border border-slate-800/60 bg-[#121218] hover:bg-[#15151c] transition-colors group">

                      <div className="flex items-center gap-4">
                        {/* Icon */}
                        <div className="shrink-0">
                          {vuln.severity === "critical" || vuln.severity === "high" ? (
                            <AlertTriangle className={`h-5 w-5 ${vuln.severity === "critical" ? "text-red-500" : "text-orange-500"}`} />
                          ) : (
                            <CheckCircle className="h-5 w-5 text-blue-500" />
                          )}
                        </div>

                        {/* Title & Engine */}
                        <div>
                          <h4 className="text-slate-200 font-semibold">{vuln.vulnerability_name}</h4>
                          <p className="text-xs text-slate-500 mt-0.5 font-mono">Engine: {vuln.vulnerability_type || "Generic_Scanner"}</p>
                        </div>
                      </div>

                      <div className="flex items-center gap-4">
                        {/* CVSS Score */}
                        {(vuln.cvss_score > 0 || (vuln.severity as string) !== 'info') && (
                          <div className="flex flex-col items-end mr-2">
                            <span className="text-[9px] uppercase font-bold text-slate-500 tracking-wider">CVSS</span>
                            <span className="text-sm font-bold font-mono text-slate-300">
                              {vuln.cvss_score > 0 ? vuln.cvss_score.toFixed(1) : "N/A"}
                            </span>
                          </div>
                        )}

                        {/* Severity Badge */}
                        <div className={`px-2.5 py-0.5 rounded text-[11px] font-bold uppercase tracking-wider
                          ${vuln.severity === 'critical' ? 'bg-red-500/10 text-red-500' :
                            vuln.severity === 'high' ? 'bg-orange-500/10 text-orange-500' :
                              vuln.severity === 'medium' ? 'bg-blue-500/10 text-blue-400' :
                                'bg-slate-500/10 text-slate-400'
                          }
                        `}>
                          {vuln.severity}
                        </div>

                        {/* Time Mock (since we only have started_at, we can just put a generic timestamp format or derived) */}
                        <div className="text-xs text-slate-600 font-mono w-16 text-right">
                          {new Date(vuln.created_at || scan.started_at).toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Bottom Progress Bar */}
            <div className="h-16 border-t border-slate-800/80 bg-[#111115] shrink-0 p-4 flex flex-col justify-center">
              <div className="w-full bg-slate-900 rounded-full h-1.5 mb-2 overflow-hidden border border-slate-800/50">
                <div
                  className="bg-purple-600 h-1.5 rounded-full transition-all duration-1000 ease-out relative"
                  style={{ width: isRunning ? '67%' : '100%' }}
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent w-full animate-[shimmer_2s_infinite]"></div>
                </div>
              </div>
              <div className="flex justify-between items-center text-xs text-slate-500 font-mono">
                <span>{isRunning ? "Analyzing payloads..." : "Scan completed"}</span>
                <span className={isRunning ? "text-slate-300" : "text-emerald-500"}>{isRunning ? "67%" : "100%"}</span>
              </div>
            </div>

          </div>
        </div>
      </div>

      <style dangerouslySetInnerHTML={{
        __html: `
        @keyframes shimmer {
          100% { transform: translateX(100%); }
        }
      `}} />
    </div>
  )
}

function Button({ className, children, onClick }: any) {
  return (
    <button
      onClick={onClick}
      className={`px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-md text-sm transition-colors ${className}`}
    >
      {children}
    </button>
  )
}
