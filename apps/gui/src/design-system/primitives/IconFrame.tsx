import type { ReactElement, ReactNode } from "react";
import "./IconFrame.css";

interface IconFrameProps {
  children: ReactNode;
  size?: "sm" | "md" | "lg";
  tone?: "critical" | "caution" | "review" | "integrity" | "unknown" | "muted";
}

/**
 * Sizing/tone wrapper for an inline SVG icon (see design-system/icons.tsx).
 * One meaning: present one icon, inheriting a single status tone via
 * currentColor. Never used to imply a status on its own — the icon always
 * accompanies a label.
 */
export function IconFrame({ children, size = "md", tone = "muted" }: IconFrameProps): ReactElement {
  return <span className={`icon-frame icon-frame--${size} icon-frame--${tone}`}>{children}</span>;
}
