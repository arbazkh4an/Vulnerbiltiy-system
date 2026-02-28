"use client"

import { cn } from "@/lib/utils"

interface LoadingSkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "text" | "circular" | "rectangular"
  width?: string | number
  height?: string | number
  lines?: number
}

function SkeletonBase({
  className,
  variant = "rectangular",
  style,
  ...props
}: React.ComponentProps<"div"> & { variant?: "text" | "circular" | "rectangular" }) {
  const baseStyles = cn(
    "animate-pulse bg-slate-700/50",
    variant === "circular" && "rounded-full",
    variant === "text" && "rounded h-4",
    variant === "rectangular" && "rounded-md",
    className
  )

  return <div className={baseStyles} style={style} {...props} />
}

export function LoadingSkeleton({
  className,
  width,
  height,
  variant = "rectangular",
  lines,
  ...props
}: LoadingSkeletonProps) {
  const style: React.CSSProperties = {
    width: width ?? (variant === "circular" ? 40 : "100%"),
    height: height ?? (variant === "text" ? 16 : variant === "circular" ? 40 : 100),
  }

  if (lines && lines > 1) {
    return (
      <div className={cn("space-y-2", className)} {...props}>
        {Array.from({ length: lines }).map((_, i) => (
          <SkeletonBase
            key={i}
            variant={variant}
            style={{
              ...style,
              width: i === lines - 1 ? "75%" : "100%",
            }}
          />
        ))}
      </div>
    )
  }

  return <SkeletonBase variant={variant} className={className} style={{ ...style, ...props.style }} {...props} />
}

export function CardSkeleton({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn("bg-slate-800/50 border border-slate-700 rounded-lg p-4 space-y-3", className)} {...props}>
      <LoadingSkeleton height={20} width="60%" />
      <LoadingSkeleton variant="text" lines={2} />
      <div className="flex gap-2 pt-2">
        <LoadingSkeleton width={60} height={24} />
        <LoadingSkeleton width={60} height={24} />
      </div>
    </div>
  )
}

export function TableRowSkeleton({ columns = 4, className, ...props }: { columns?: number } & React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn("flex gap-4 py-3 border-b border-slate-800", className)} {...props}>
      {Array.from({ length: columns }).map((_, i) => (
        <LoadingSkeleton key={i} height={16} width={Math.random() * 40 + 60} />
      ))}
    </div>
  )
}

export function ChartSkeleton({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn("bg-slate-800/50 border border-slate-700 rounded-lg p-4 space-y-3", className)} {...props}>
      <LoadingSkeleton height={20} width={120} />
      <div className="flex items-end gap-1 h-32">
        {Array.from({ length: 12 }).map((_, i) => (
          <LoadingSkeleton
            key={i}
            width="100%"
            height={`${Math.random() * 60 + 20}%`}
            className="flex-1"
          />
        ))}
      </div>
    </div>
  )
}

export function ProfileSkeleton({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn("flex items-center gap-4", className)} {...props}>
      <LoadingSkeleton variant="circular" width={48} height={48} />
      <div className="space-y-2 flex-1">
        <LoadingSkeleton height={16} width="40%" />
        <LoadingSkeleton variant="text" height={12} width="25%" />
      </div>
    </div>
  )
}

export function ScanListSkeleton({ count = 3, className, ...props }: { count?: number } & React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn("space-y-3", className)} {...props}>
      {Array.from({ length: count }).map((_, i) => (
        <CardSkeleton key={i} />
      ))}
    </div>
  )
}
