// Small inline SVG icons used across the brand UI.

export function BrandMark({ className }) {
  return (
    <span className={className ?? "mark"}>
      <svg viewBox="0 0 32 32" fill="none" aria-hidden="true">
        <rect width="32" height="32" rx="9" fill="var(--primary, #3b82f6)" />
        <path
          d="M4 12v8M10 7v18M16 4v24M22 7v18M28 12v8"
          stroke="#fff"
          strokeWidth="3"
          strokeLinecap="round"
        />
      </svg>
    </span>
  );
}

export function MicIcon() {
  return (
    <svg viewBox="0 0 256 256" fill="none" stroke="currentColor" strokeWidth="18" strokeLinecap="round" strokeLinejoin="round">
      <rect x="88" y="40" width="80" height="112" rx="32" />
      <path d="M192,128a64,64,0,0,1-128,0" />
      <line x1="128" y1="192" x2="128" y2="224" />
      <line x1="88" y1="224" x2="168" y2="224" />
    </svg>
  );
}

export function UserIcon() {
  return (
    <svg viewBox="0 0 256 256" fill="none" stroke="currentColor" strokeWidth="18" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="128" cy="104" r="40" />
      <path d="M64,216c8-28.5,35.4-48,64-48s56,19.5,64,48" />
    </svg>
  );
}

export function ArrowIcon() {
  return (
    <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" width="1em" height="1em">
      <path d="M2 8h11M9 3l5 5-5 5" />
    </svg>
  );
}

export function StepsIcon({ step }) {
  const common = {
    viewBox: "0 0 256 256",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 18,
    strokeLinecap: "round",
    strokeLinejoin: "round",
  };
  switch (step) {
    case 1:
      return (
        <svg {...common}>
          <circle cx="128" cy="104" r="40" />
          <path d="M64,216c8-28.5,35.4-48,64-48s56,19.5,64,48" />
        </svg>
      );
    case 2:
      return (
        <svg {...common}>
          <path d="M48,96H208a16,16,0,0,1,16,16V192a16,16,0,0,1-16,16H88l-56,32V112A16,16,0,0,1,48,96Z" />
          <path d="M96,80V72a32,32,0,0,1,64,0v8" />
          <line x1="104" y1="144" x2="152" y2="144" />
        </svg>
      );
    case 3:
      return (
        <svg {...common}>
          <path d="M128,152a24,24,0,0,1-36,36L64,160a24,24,0,0,1,36-36" />
          <path d="M156,72a24,24,0,0,1,36,36l-28,28a24,24,0,0,1-36-36" />
        </svg>
      );
    case 4:
      return (
        <svg {...common}>
          <polyline points="40,132 96,188 216,68" />
        </svg>
      );
    default:
      return null;
  }
}

export function DemoCardIcon({ kind }) {
  const common = {
    viewBox: "0 0 256 256",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 18,
    strokeLinecap: "round",
    strokeLinejoin: "round",
  };
  switch (kind) {
    case "hospitals":
      return (
        <svg {...common}>
          <path d="M128,60v136" />
          <path d="M60,128h136" />
        </svg>
      );
    case "enterprises":
      return (
        <svg {...common}>
          <path d="M96,224V88a8,8,0,0,1,8-8h48a8,8,0,0,1,8,8V224" />
          <path d="M40,224H216" />
          <path d="M112,120h8M136,120h8M112,152h8M136,152h8M112,184h8M136,184h8" />
        </svg>
      );
    case "stores":
      return (
        <svg {...common}>
          <path d="M56,104v88a8,8,0,0,0,8,8H192a8,8,0,0,0,8-8V104" />
          <path d="M40,64l14-28a8,8,0,0,1,7-4h134a8,8,0,0,1,7,4l14,28" />
          <path d="M168,216V160a8,8,0,0,0-8-8H96a8,8,0,0,0-8,8v56" />
          <path d="M40,64H216v24a16,16,0,0,1-16,16A16,16,0,0,1,184,104a16,16,0,0,1-16-16,16,16,0,0,1-16,16,16,16,0,0,1-16-16,16,16,0,0,1-16,16,16,16,0,0,1-16-16,16,16,0,0,1-16,16,16,16,0,0,1-16-16,16,16,0,0,1-16-16Z" />
        </svg>
      );
    default:
      return null;
  }
}
