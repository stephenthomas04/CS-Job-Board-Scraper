import type { ReactNode } from "react";

interface PillProps {
  children: ReactNode;
  /** Optional leading icon (rendered in teal). */
  icon?: ReactNode;
  className?: string;
  title?: string;
}

export default function Pill({ children, icon, className = "", title }: PillProps) {
  return (
    <span
      title={title}
      className={`inline-flex items-center gap-1.5 rounded-full border border-gray-200 bg-gray-50 text-gray-700 text-sm font-medium px-3.5 py-2 whitespace-nowrap ${className}`}
    >
      {icon ? <span className="text-cyan-600">{icon}</span> : null}
      {children}
    </span>
  );
}
