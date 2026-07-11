import type { ButtonHTMLAttributes, ReactElement } from "react";
import "./Button.css";

type ButtonVariant = "primary" | "secondary" | "danger";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
}

/**
 * Per docs/design/COMPONENT_RULES.md §17-19: one primary action per screen,
 * verb-first labels, never green, never an approval affordance. There is no
 * "Approve" / "Sign off" / "Certify" / "Release" variant — the product does
 * not capture or infer human approval, so no such button exists to build.
 */
export function Button({ variant = "secondary", className = "", ...rest }: ButtonProps): ReactElement {
  return <button className={`btn btn--${variant} ${className}`.trim()} {...rest} />;
}
