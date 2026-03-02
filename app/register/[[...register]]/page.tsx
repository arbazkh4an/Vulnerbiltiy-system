"use client"

import { SignUp } from "@clerk/nextjs"
import { Shield } from "lucide-react"
import Link from "next/link"

export default function RegisterPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 relative overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-emerald-900/20 via-transparent to-transparent pointer-events-none" />

      <div className="relative z-10 w-full max-w-md px-4">
        <div className="flex flex-col items-center mb-8">
          <Link href="/" className="flex items-center gap-2 mb-4">
            <Shield className="h-10 w-10 text-emerald-400" />
            <span className="text-2xl font-bold text-slate-100">VulnScan AI</span>
          </Link>
          <h1 className="text-xl text-slate-300">Create an account</h1>
          <p className="text-sm text-slate-500 mt-1">Get started with vulnerability scanning</p>
        </div>

        <div className="bg-slate-900/80 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 shadow-2xl">
          <SignUp
            appearance={{
              elements: {
                rootBox: "w-full",
                card: "bg-transparent shadow-none",
                formButtonPrimary: "bg-emerald-600 hover:bg-emerald-700 text-white",
                formButtonSecondary: "bg-slate-700 hover:bg-slate-600 text-slate-200",
                footerActionLink: "text-emerald-400 hover:text-emerald-300",
                dividerLine: "bg-slate-700",
                dividerText: "text-slate-500",
                identityPreviewText: "text-slate-300",
                identityPreviewEditButton: "text-emerald-400 hover:text-emerald-300",
                formFieldInput: "bg-slate-800 border-slate-700 text-slate-100",
                formFieldLabel: "text-slate-400",
                formFieldInputShowPasswordButton: "text-slate-400",
                otpCodeFieldInput: "bg-slate-800 border-slate-700 text-slate-100",
                footer: "hidden",
                headerTitle: "hidden",
                headerSubtitle: "hidden",
                socialButtonsBlockButton: "bg-slate-800 border-slate-700 hover:bg-slate-700 text-slate-200",
                socialButtonsBlockButtonText: "text-slate-200",
                formFieldInputFocus: "border-emerald-500 ring-emerald-500/20",
              },
            }}
            routing="path"
            path="/register"
            signInUrl="/login"
            fallbackRedirectUrl="/dashboard"
          />
        </div>

        <p className="text-center text-sm text-slate-500 mt-6">
          Already have an account?{" "}
          <Link href="/login" className="text-emerald-400 hover:text-emerald-300 font-medium">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  )
}
