import { SiteHeader } from "@/components/site-header"
import { HeroSection } from "@/components/hero-section"
import { FeaturesSection } from "@/components/features-section"
import { ScannersSection } from "@/components/scanners-section"
import { MethodologySection } from "@/components/methodology-section"
import { PricingSection } from "@/components/pricing-section"

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col bg-background text-foreground selection:bg-purple-500/30">
      <SiteHeader />
      <main className="flex-1">
        <HeroSection />
        <FeaturesSection />
        <ScannersSection />
        <MethodologySection />
        <PricingSection />
      </main>
      <footer className="py-8 border-t border-white/10 mt-auto bg-black/40">
        <div className="container text-center">
          <div className="flex justify-center space-x-6 mb-4 text-sm text-muted-foreground">
            <a href="#" className="hover:text-foreground">Privacy Policy</a>
            <a href="#" className="hover:text-foreground">Terms of Service</a>
            <a href="#" className="hover:text-foreground">Contact</a>
          </div>
          <p className="text-sm text-muted-foreground">&copy; {new Date().getFullYear()} VulnScan AI. Built for FYP 2025.</p>
        </div>
      </footer>
    </div>
  )
}
