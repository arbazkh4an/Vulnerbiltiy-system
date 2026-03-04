"use client"

import { useState } from "react"
import { pdf } from "@react-pdf/renderer"
import { VulnerabilityReportDocument } from "./VulnerabilityReportDocument"
import { Download, Loader2 } from "lucide-react"
import type { Scan, Vulnerability } from "@/lib/types"

interface Props {
  scan: Scan
  vulnerabilities: Vulnerability[]
}

export default function DownloadReportButton({ scan, vulnerabilities }: Props) {
  const [loading, setLoading] = useState(false)

  const handleDownload = async () => {
    setLoading(true)
    try {
      // Map Scan type to match what VulnerabilityReportDocument expects
      const scanForPdf = {
        ...scan,
        started_at: scan.started_at ? new Date(scan.started_at) : null,
        completed_at: scan.completed_at ? new Date(scan.completed_at) : null,
        user_name: (scan as any).user_name ?? null,
        user_email: (scan as any).user_email ?? null,
      }

      const blob = await pdf(
        <VulnerabilityReportDocument scan={scanForPdf as any} vulnerabilities={vulnerabilities as any} />
      ).toBlob()

      const url = URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = `vulnscan-report-${scan.id}.pdf`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } catch (err) {
      console.error("PDF generation failed:", err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <button
      onClick={handleDownload}
      disabled={loading}
      className="flex items-center gap-2 px-4 py-2 bg-emerald-600/10 hover:bg-emerald-600/20 disabled:opacity-50 text-emerald-400 rounded-md text-sm transition-colors border border-emerald-500/30 font-medium font-mono whitespace-nowrap cursor-pointer disabled:cursor-not-allowed"
    >
      {loading ? (
        <>
          <Loader2 className="h-4 w-4 animate-spin" />
          GENERATING...
        </>
      ) : (
        <>
          <Download className="h-4 w-4" />
          DOWNLOAD PDF REPORT
        </>
      )}
    </button>
  )
}
