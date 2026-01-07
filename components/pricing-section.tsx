"use client"

import { motion } from "framer-motion"
import { Check } from "lucide-react"
import { Button } from "@/components/ui/button"

export function PricingSection() {
    const plans = [
        {
            name: "Starter",
            price: "$0",
            description: "For individual developers testing local apps.",
            features: ["5 Scans per month", "Basic OWASP detection", "HTML Reports", "Community Support"]
        },
        {
            name: "Pro",
            price: "$49",
            description: "For small teams and startups.",
            popular: true,
            features: ["Unlimited Scans", "Full OWASP Top 10", "AI Severity Analysis", "PDF & JSON Exports", "Priority Support"]
        },
        {
            name: "Enterprise",
            price: "Custom",
            description: "For large organizations with compliance needs.",
            features: ["SSO Integration", "On-premise Deployment", "Custom Scan Engines", "API Access", "Dedicated Account Manager"]
        }
    ]

    return (
        <section id="pricing" className="py-24 relative overflow-hidden">
            {/* Background glow for pricing */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-violet-500/10 rounded-full blur-[120px] -z-10" />

            <div className="container px-4 md:px-6">
                <div className="text-center mb-16">
                    <h2 className="text-3xl font-bold tracking-tight sm:text-4xl mb-4">
                        Simple, Transparent Pricing
                    </h2>
                    <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
                        Start Securing your applications today. No credit card required.
                    </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    {plans.map((plan, index) => (
                        <motion.div
                            key={plan.name}
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.5, delay: index * 0.1 }}
                            viewport={{ once: true }}
                            className={`relative flex flex-col p-8 rounded-2xl border ${plan.popular
                                    ? "bg-white/5 border-primary/50 shadow-2xl shadow-primary/10 scale-105 z-10"
                                    : "bg-black/20 border-white/10 hover:bg-white/5 transition-colors"
                                }`}
                        >
                            {plan.popular && (
                                <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 bg-primary text-primary-foreground text-xs font-bold rounded-full uppercase tracking-wider">
                                    Most Popular
                                </div>
                            )}

                            <h3 className="text-xl font-semibold mb-2">{plan.name}</h3>
                            <div className="flex items-baseline mb-4">
                                <span className="text-3xl font-bold">{plan.price}</span>
                                {plan.price !== "Custom" && <span className="text-muted-foreground ml-1">/month</span>}
                            </div>
                            <p className="text-sm text-muted-foreground mb-6">{plan.description}</p>

                            <div className="space-y-3 mb-8 flex-1">
                                {plan.features.map((feature) => (
                                    <div key={feature} className="flex items-center text-sm">
                                        <Check className="h-4 w-4 text-primary mr-2 flex-shrink-0" />
                                        {feature}
                                    </div>
                                ))}
                            </div>

                            <Button className={`w-full ${plan.popular ? "bg-primary hover:bg-primary/90" : "bg-white/10 hover:bg-white/20"} rounded-lg h-10`}>
                                {plan.name === "Enterprise" ? "Contact Sales" : "Get Started"}
                            </Button>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    )
}
