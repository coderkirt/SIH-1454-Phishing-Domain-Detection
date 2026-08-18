export default function DotMatrixLogo({ size = "md", className = "" }) {
  const dim = size === "sm" ? 22 : 34;

  return (
    <svg
      width={dim}
      height={dim}
      viewBox="0 0 32 32"
      fill="none"
      className={className}
      aria-hidden="true"
    >
      <path
        d="M16 3L27 8.2v8.1c0 7.2-5.3 12.4-11 14.7C10.3 28.7 5 23.5 5 16.3V8.2L16 3z"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinejoin="round"
      />
      <path
        d="M8.5 16c2.4-4.2 5.2-6.3 7.5-6.3S21.1 11.8 23.5 16c-2.4 4.2-5.2 6.3-7.5 6.3S10.9 20.2 8.5 16z"
        stroke="currentColor"
        strokeWidth="1.4"
      />
      <circle cx="16" cy="16" r="2.6" fill="#ff0000" />
      <circle cx="16.8" cy="15.2" r="0.7" fill="#fff" />
    </svg>
  );
}
