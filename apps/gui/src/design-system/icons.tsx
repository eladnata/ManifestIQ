import type { ReactElement, SVGProps } from "react";

/**
 * ManifestIQ icon set. Inline SVG only — no external icon runtime, no font
 * icons, no CDN. Line/stroke style, monochrome, inherits currentColor so
 * icons never carry status color independently of their surrounding label.
 *
 * The vocabulary is deliberately drawn from the evidence world (seal,
 * ledger, fingerprint) per docs/design/VISUAL_TASTE_DOCTRINE.md §8 —
 * no illustration, no mascots, no emoji.
 */

type IconProps = SVGProps<SVGSVGElement> & { size?: number };

function base(props: IconProps, children: ReactElement) {
  const { size = 16, ...rest } = props;
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.6}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      focusable="false"
      {...rest}
    >
      {children}
    </svg>
  );
}

/** Evidence-integrity seal. Used only where evidence integrity is being represented. */
export function SealIcon(props: IconProps): ReactElement {
  return base(
    props,
    <>
      <path d="M12 2.5 4.5 6v6c0 4.5 3.2 7.3 7.5 9.5 4.3-2.2 7.5-5 7.5-9.5V6z" />
      <path d="M8.5 12.2 11 14.7l4.5-5" />
    </>,
  );
}

/** Ledger / manifest mark. Used for evidence lists and provenance. */
export function LedgerIcon(props: IconProps): ReactElement {
  return base(
    props,
    <>
      <rect x="5" y="3" width="14" height="18" rx="1.5" />
      <path d="M8.5 8h7M8.5 12h7M8.5 16h4" />
    </>,
  );
}

/** Fingerprint / provenance mark. Used for run manifest hash references. */
export function FingerprintIcon(props: IconProps): ReactElement {
  return base(
    props,
    <>
      <path d="M12 3.5c-4.7 0-8.5 3.8-8.5 8.5 0 2.6.6 4.6 1.4 6.1" />
      <path d="M12 3.5c4.7 0 8.5 3.8 8.5 8.5 0 1-.1 2-.3 2.9" />
      <path d="M12 7.5a4.5 4.5 0 0 0-4.5 4.5c0 3 1 5 2.2 6.7" />
      <path d="M12 7.5a4.5 4.5 0 0 1 4.5 4.5c0 1.6-.2 2.9-.6 4" />
      <path d="M12 11.5a.5.5 0 1 0 0 .001" />
      <path d="M12 11.5c0 2.6.7 4.6 1.8 6.3" />
    </>,
  );
}

/** Empty-slot mark for the permanently absent human-approval layer. */
export function EmptySlotIcon(props: IconProps): ReactElement {
  return base(
    props,
    <>
      <rect x="4" y="4" width="16" height="16" rx="2" strokeDasharray="3 3" />
    </>,
  );
}

/** Chevron used for the minimal disclosure interaction on blocker cards. */
export function ChevronIcon(props: IconProps): ReactElement {
  return base(props, <path d="M9 6l6 6-6 6" />);
}
