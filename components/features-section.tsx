"use client"

import { motion } from "framer-motion"
import { ShieldAlert, Zap, FileText, Lock, Activity, Brain } from "lucide-react"

const features = [
    {
        title: "OWASP Top 10:2025",
        description: "Comprehensive scanning for the latest critical web application security risks.",
        icon: ShieldAlert,
        colSpan: "lg:col-span-2",
        delay: 0.1
    },
    {
        title: "AI Severity Prediction",
        description: "Machine learning models analyze context to predict true risk levels.",
        icon: Brain,
        colSpan: "lg:col-span-1",
        delay: 0.2
    },
    {
        title: "Instant Reports",
        description: "Generate detailed PDF remediation guides with one click.",
        icon: FileText,
        colSpan: "lg:col-span-1",
        delay: 0.3
    },
    {
        title: "Real-time Monitoring",
        description: "Watch scans progress in real-time with live socket updates.",
        icon: Activity,
        colSpan: "lg:col-span-2",
        delay: 0.4
    },
]

export function FeaturesSection() {
    return (
        <section className="py-24 bg-black/20">
            <div className="container px-4 md:px-6">
                <div className="text-center mb-16">
                    <h2 className="text-3xl font-bold tracking-tight sm:text-4xl mb-4">
                        Advanced Vulnerability Detection
                    </h2>
                    <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
                        Our dual-engine approach combines traditional heuristic scanning with
                        state-of-the-art machine learning analysis.
                    </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {features.map((feature, index) => (
                        <motion.div
                            key={feature.title}
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.5, delay: feature.delay }}
                            viewport={{ once: true }}
                            className={`glass-card p-8 hover:bg-white/10 transition-colors ${feature.colSpan}`}
                        >
                            <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-6">
                                <feature.icon className="h-6 w-6 text-indigo-400" />
                            </div>
                            <h3 className="text-xl font-semibold mb-3">{feature.title}</h3>
                            <p className="text-muted-foreground leading-relaxed">
                                {feature.description}
                            </p>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    )
}
