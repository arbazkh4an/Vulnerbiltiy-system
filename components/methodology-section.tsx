"use client"

import { motion } from "framer-motion"
import { Database, Search, BrainCircuit, FileCheck } from "lucide-react"

export function MethodologySection() {
    const steps = [
        {
            icon: Search,
            title: "Discovery",
            description: "Crawls the target application to map all endpoints and input vectors."
        },
        {
            icon: Database,
            title: "Injection",
            description: "Tests thousands of safe payloads against identified inputs."
        },
        {
            icon: BrainCircuit,
            title: "AI Analysis",
            description: "Machine learning models evaluate response patterns to confirm vulnerabilities."
        },
        {
            icon: FileCheck,
            title: "Reporting",
            description: "Generates a CVSS-scored PDF report with remediation steps."
        }
    ]

    return (
        <section id="methodology" className="py-24 bg-black/40">
            <div className="container px-4 md:px-6">
                <div className="text-center mb-16">
                    <h2 className="text-3xl font-bold tracking-tight sm:text-4xl mb-4">
                        How It Works
                    </h2>
                    <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
                        From initial crawl to final report, our autonomous agent handles the entire security lifecycle.
                    </p>
                </div>

                <div className="relative">
                    {/* Connecting Line (Desktop) */}
                    <div className="absolute top-1/2 left-0 w-full h-0.5 bg-gradient-to-r from-transparent via-white/10 to-transparent hidden md:block -translate-y-1/2" />

                    <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
                        {steps.map((step, index) => (
                            <motion.div
                                key={step.title}
                                initial={{ opacity: 0, y: 20 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.5, delay: index * 0.1 }}
                                viewport={{ once: true }}
                                className="relative z-10 flex flex-col items-center text-center group"
                            >
                                <div className="h-16 w-16 rounded-2xl bg-black border border-white/10 flex items-center justify-center mb-6 group-hover:border-primary/50 group-hover:shadow-[0_0_30px_-5px_hsl(var(--primary))] transition-all duration-300">
                                    <step.icon className="h-8 w-8 text-muted-foreground group-hover:text-primary transition-colors" />
                                </div>
                                <h3 className="text-lg font-semibold mb-2">{step.title}</h3>
                                <p className="text-sm text-muted-foreground">
                                    {step.description}
                                </p>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </div>
        </section>
    )
}
