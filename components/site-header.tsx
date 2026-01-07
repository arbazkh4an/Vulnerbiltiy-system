"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Shield } from "lucide-react"
import { motion } from "framer-motion"

export function SiteHeader() {
    const scrollToSection = (e: React.MouseEvent<HTMLAnchorElement>, id: string) => {
        e.preventDefault()
        const element = document.getElementById(id)
        if (element) {
            element.scrollIntoView({ behavior: 'smooth' })
        }
    }

    return (
        <motion.header
            initial={{ y: -20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            className="sticky top-0 z-50 w-full border-b border-white/5 bg-background/60 backdrop-blur-xl supports-[backdrop-filter]:bg-background/60"
        >
            <div className="container flex h-16 items-center px-4 md:px-6">
                <Link href="/" className="mr-6 flex items-center space-x-2">
                    <Shield className="h-6 w-6 text-foreground" />
                    <span className="font-bold text-lg tracking-tight">VulnScan AI</span>
                </Link>
                <nav className="hidden md:flex flex-1 items-center justify-center space-x-8 text-sm font-medium text-muted-foreground">
                    <a href="#scanners" onClick={(e) => scrollToSection(e, 'scanners')} className="transition-colors hover:text-foreground">
                        Scanners
                    </a>
                    <a href="#methodology" onClick={(e) => scrollToSection(e, 'methodology')} className="transition-colors hover:text-foreground">
                        Methodology
                    </a>
                    <a href="#pricing" onClick={(e) => scrollToSection(e, 'pricing')} className="transition-colors hover:text-foreground">
                        Pricing
                    </a>
                </nav>
                <div className="ml-auto w-auto flex items-center space-x-4">
                    <Link href="/login" className="text-sm font-medium text-muted-foreground hover:text-foreground">
                        Log in
                    </Link>
                    <Button asChild className="rounded-full bg-primary text-primary-foreground hover:bg-primary/90 px-6">
                        <Link href="/register">Get Started</Link>
                    </Button>
                </div>
            </div>
        </motion.header>
    )
}
