import type { ReactElement, ReactNode } from "react";
import "../surfaces.css";

type SurfaceTone = "critical" | "caution" | "review" | undefined;

interface SurfaceProps {
  children: ReactNode;
  variant?: "flush" | "raised" | "inset" | "hero";
  tone?: SurfaceTone;
  as?: "div" | "section";
  className?: string;
  ariaLabel?: string;
}

/**
 * Structural card/panel primitive. One meaning: a bounded surface with
 * restrained elevation. Callers choose one job for the surface to do —
 * this primitive never becomes a multi-purpose container.
 */
export function Surface({
  children,
  variant,
  tone,
  as = "div",
  className = "",
  ariaLabel,
}: SurfaceProps): ReactElement {
  const Tag = as;
  const classes = [
    "surface",
    variant ? `surface--${variant}` : "",
    tone ? `tone-${tone}` : "",
    className,
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <Tag className={classes} aria-label={ariaLabel}>
      {children}
    </Tag>
  );
}
