"use client"

import * as React from "react"
import { Moon, Sun } from "lucide-react"
import { useTheme } from "next-themes"
import { motion } from "framer-motion"

import { Button } from "@/components/ui/button"

export function ModeToggle() {
    const { theme, setTheme } = useTheme()
    const [mounted, setMounted] = React.useState(false)
    const [isLoading, setIsLoading] = React.useState(false)

    // Avoid hydration mismatch
    React.useEffect(() => {
        setMounted(true)
    }, [])

    const handleThemeToggle = async () => {
        setIsLoading(true)
        setTheme(theme === "dark" ? "light" : "dark")
        setTimeout(() => setIsLoading(false), 200)
    }

    if (!mounted) {
        return <Button variant="ghost" size="icon" disabled aria-label="Loading theme" />
    }

    const isDark = theme === "dark"

    return (
        <Button
            variant="ghost"
            size="icon"
            onClick={handleThemeToggle}
            disabled={isLoading}
            className="relative h-10 w-10 rounded-full"
            aria-label={isLoading ? "Theme changing" : "Toggle theme"}
        >
            <motion.div
                initial={false}
                animate={{
                    scale: isDark ? 0 : 1,
                    rotate: isDark ? 90 : 0,
                    opacity: isDark ? 0 : 1
                }}
                transition={{ duration: 0.2, ease: "easeInOut" }}
                className="absolute"
            >
                <Sun className="h-[1.2rem] w-[1.2rem]" />
            </motion.div>
            <motion.div
                initial={false}
                animate={{
                    scale: isDark ? 1 : 0,
                    rotate: isDark ? 0 : -90,
                    opacity: isDark ? 1 : 0
                }}
                transition={{ duration: 0.2, ease: "easeInOut" }}
                className="absolute"
            >
                <Moon className="h-[1.2rem] w-[1.2rem]" />
            </motion.div>
            <span className="sr-only">Toggle theme</span>
        </Button>
    )
}
