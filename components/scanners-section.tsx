"use client"

import { motion } from "framer-motion"
import { Shield, Search, Terminal, AlertTriangle, CheckCircle } from "lucide-react"

export function ScannersSection() {
    return (
        <section id="scanners" className="py-24 relative overflow-hidden">
            <div className="container px-4 md:px-6">
                <div className="flex flex-col items-center text-center mb-16">
                    <h2 className="text-3xl font-bold tracking-tight sm:text-4xl mb-4">
                        Powerful Scanning Engines
                    </h2>
                    <p className="text-muted-foreground text-lg max-w-2xl">
                        Visualize your security posture with our advanced scanning dashboard.
                        Detecting SQLi, XSS, and more in real-time.
                    </p>
                </div>

                {/* Mockup Window */}
                <motion.div
                    initial={{ opacity: 0, y: 40 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.7 }}
                    viewport={{ once: true }}
                    className="relative max-w-5xl mx-auto"
                >
                    <div className="rounded-xl border border-white/10 bg-black/40 backdrop-blur-xl shadow-2xl overflow-hidden">
                        {/* Window Header */}
                        <div className="flex items-center px-4 py-3 border-b border-white/5 bg-white/5">
                            <div className="flex space-x-2">
                                <div className="h-3 w-3 rounded-full bg-red-500/20 md:bg-red-500" />
                                <div className="h-3 w-3 rounded-full bg-yellow-500/20 md:bg-yellow-500" />
                                <div className="h-3 w-3 rounded-full bg-green-500/20 md:bg-green-500" />
                            </div>
                            <div className="mx-auto text-xs font-mono text-muted-foreground">vulnscan-dashboard.exe</div>
                        </div>

                        {/* Window Content */}
                        <div className="grid grid-cols-1 md:grid-cols-4 min-h-[500px]">
                            {/* Sidebar */}
                            <div className="hidden md:block border-r border-white/5 bg-white/5 p-4 space-y-4">
                                <div className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">Targets</div>
                                <div className="flex items-center p-2 rounded-md bg-primary/10 text-primary text-sm font-medium">
                                    <Shield className="h-4 w-4 mr-2" />
                                    production-api
                                </div>
                                <div className="flex items-center p-2 rounded-md hover:bg-white/5 text-muted-foreground text-sm cursor-not-allowed">
                                    <Shield className="h-4 w-4 mr-2" />
                                    staging-server
                                </div>

                                <div className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mt-6 mb-2">Engines</div>
                                <div className="space-y-1">
                                    {['SQL Injection', 'XSS Scanner', 'CSRF Detection', 'Auth Bypass'].map((item) => (
                                        <div key={item} className="flex items-center p-2 text-sm text-muted-foreground">
                                            <Terminal className="h-3 w-3 mr-2" /> {item}
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {/* Main Area */}
                            <div className="col-span-3 p-6">
                                <div className="flex justify-between items-center mb-6">
                                    <h3 className="text-xl font-semibold">Live Scan Results</h3>
                                    <div className="flex items-center space-x-2">
                                        <span className="flex h-2 w-2 rounded-full bg-green-500 animate-pulse" />
                                        <span className="text-xs text-green-500 font-mono">SCANNING ACTIVE</span>
                                    </div>
                                </div>

                                <div className="space-y-4">
                                    {[
                                        { type: "SQL Injection", severity: "Critical", time: "10:42:01", status: "detected" },
                                        { type: "Reflected XSS", severity: "High", time: "10:42:05", status: "detected" },
                                        { type: "Missing Headers", severity: "Low", time: "10:42:08", status: "info" },
                                        { type: "Open Port 5432", severity: "Medium", time: "10:42:12", status: "warning" },
                                    ].map((log, i) => (
                                        <div key={i} className="flex items-center justify-between p-3 rounded-lg border border-white/5 bg-black/20 hover:bg-white/5 transition-colors">
                                            <div className="flex items-center space-x-3">
                                                {log.severity === "Critical" ? <AlertTriangle className="h-5 w-5 text-red-500" /> :
                                                    log.severity === "High" ? <AlertTriangle className="h-5 w-5 text-orange-500" /> :
                                                        <CheckCircle className="h-5 w-5 text-blue-500" />}
                                                <div>
                                                    <p className="font-medium text-sm">{log.type}</p>
                                                    <p className="text-xs text-muted-foreground font-mono">Engine: {log.type.split(' ')[0]}_V2</p>
                                                </div>
                                            </div>
                                            <div className="flex flex-col items-end">
                                                <span className={`text-xs px-2 py-0.5 rounded-full ${log.severity === "Critical" ? "bg-red-500/10 text-red-500" :
                                                        log.severity === "High" ? "bg-orange-500/10 text-orange-500" :
                                                            "bg-blue-500/10 text-blue-500"
                                                    }`}>
                                                    {log.severity}
                                                </span>
                                                <span className="text-xs text-muted-foreground mt-1 font-mono">{log.time}</span>
                                            </div>
                                        </div>
                                    ))}

                                    {/* Fake loading bars */}
                                    <div className="space-y-2 pt-4">
                                        <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
                                            <div className="h-full bg-indigo-500 w-2/3 animate-[shimmer_2s_infinite]" />
                                        </div>
                                        <div className="flex justify-between text-xs text-muted-foreground">
                                            <span>Analyzing payloads...</span>
                                            <span>67%</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Decorative Elements behind window */}
                    <div className="absolute -z-10 -top-20 -right-20 h-64 w-64 bg-violet-500/20 rounded-full blur-[100px]" />
                    <div className="absolute -z-10 -bottom-20 -left-20 h-64 w-64 bg-blue-500/20 rounded-full blur-[100px]" />
                </motion.div>
            </div>
        </section>
    )
}
