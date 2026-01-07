"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { motion } from "framer-motion"
import { ArrowRight, CheckCircle2 } from "lucide-react"

export function HeroSection() {
    return (
        <section className="relative overflow-hidden pt-12 pb-24 lg:pt-20 lg:pb-32">
            {/* Background Blobs */}
            <div className="absolute top-0 right-0 -translate-y-1/2 translate-x-1/2 blob-purple" />
            <div className="absolute bottom-0 left-0 translate-y-1/2 -translate-x-1/2 blob-blue" />

            <div className="container px-4 md:px-6 relative z-10">
                <div className="flex flex-col items-center text-center space-y-8">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5 }}
                        className="inline-flex items-center rounded-full border border-white/10 bg-white/5 px-3 py-1 text-sm text-muted-foreground backdrop-blur"
                    >
                        <span className="flex h-2 w-2 rounded-full bg-green-500 mr-2" />
                        Active Defense System Online
                    </motion.div>

                    <motion.h1
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5, delay: 0.1 }}
                        className="text-4xl font-extrabold tracking-tight sm:text-6xl md:text-7xl lg:text-8xl max-w-4xl mx-auto"
                    >
                        Secure Your Web <br />
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-violet-500 text-glow">
                            Infrastructure
                        </span>
                    </motion.h1>

                    <motion.p
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5, delay: 0.2 }}
                        className="max-w-[700px] text-lg text-muted-foreground md:text-xl leading-relaxed"
                    >
                        Automated vulnerability scanning powered by advanced AI. Detect OWASP Top 10 threats
                        before they strike with real-time severity prediction.
                    </motion.p>

                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5, delay: 0.3 }}
                        className="flex flex-col sm:flex-row gap-4 w-full sm:w-auto"
                    >
                        <Button asChild size="lg" className="rounded-full h-12 px-8 text-base bg-white text-black hover:bg-white/90">
                            <Link href="/register">Start Scanning Free</Link>
                        </Button>
                        <Button asChild variant="outline" size="lg" className="rounded-full h-12 px-8 text-base border-white/10 hover:bg-white/5">
                            <Link href="/demo">
                                View Live Demo <ArrowRight className="ml-2 h-4 w-4" />
                            </Link>
                        </Button>
                    </motion.div>

                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ duration: 1, delay: 0.5 }}
                        className="pt-8 flex flex-wrap justify-center gap-x-8 gap-y-4 text-sm text-muted-foreground"
                    >
                        <div className="flex items-center"><CheckCircle2 className="mr-2 h-4 w-4 text-blue-500" /> OWASP Top 10</div>
                        <div className="flex items-center"><CheckCircle2 className="mr-2 h-4 w-4 text-violet-500" /> Real-time Analysis</div>
                        <div className="flex items-center"><CheckCircle2 className="mr-2 h-4 w-4 text-green-500" /> PDF Reports</div>
                    </motion.div>
                </div>
            </div>
        </section>
    )
}
