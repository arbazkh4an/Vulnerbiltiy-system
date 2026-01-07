"use client"

import { useEffect, useState } from "react"
import { useSearchParams, useRouter } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { CheckCircle2, XCircle, Loader2 } from "lucide-react"

export default function VerifyEmailPage() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading")
  const [message, setMessage] = useState("")

  useEffect(() => {
    const token = searchParams.get("token")

    if (!token) {
      setStatus("error")
      setMessage("Invalid verification link")
      return
    }

    const verifyEmail = async () => {
      try {
        const response = await fetch(`/api/auth/verify-email?token=${token}`)
        const data = await response.json()

        if (response.ok) {
          setStatus("success")
          setMessage(data.message || "Email verified successfully!")
        } else {
          setStatus("error")
          setMessage(data.error || "Verification failed")
        }
      } catch (error) {
        setStatus("error")
        setMessage("An error occurred during verification")
      }
    }

    verifyEmail()
  }, [searchParams])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-950 via-emerald-950 to-slate-950 p-4">
      <Card className="w-full max-w-md border-emerald-900/50 bg-slate-950/90 backdrop-blur">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold text-emerald-400">Email Verification</CardTitle>
          <CardDescription className="text-slate-400">Verifying your email address</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex flex-col items-center justify-center py-8">
            {status === "loading" && (
              <>
                <Loader2 className="h-16 w-16 animate-spin text-emerald-500 mb-4" />
                <p className="text-slate-300 text-center">Verifying your email...</p>
              </>
            )}

            {status === "success" && (
              <>
                <CheckCircle2 className="h-16 w-16 text-emerald-500 mb-4" />
                <p className="text-slate-300 text-center font-medium mb-2">Success!</p>
                <p className="text-slate-400 text-center text-sm">{message}</p>
              </>
            )}

            {status === "error" && (
              <>
                <XCircle className="h-16 w-16 text-red-500 mb-4" />
                <p className="text-slate-300 text-center font-medium mb-2">Verification Failed</p>
                <p className="text-slate-400 text-center text-sm">{message}</p>
              </>
            )}
          </div>

          {status !== "loading" && (
            <Button
              className="w-full bg-emerald-600 hover:bg-emerald-700"
              onClick={() => router.push(status === "success" ? "/login" : "/register")}
            >
              {status === "success" ? "Go to Login" : "Back to Register"}
            </Button>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
