import type { ReactNode } from "react";
import type { Job } from "../types";
import Pill from "./Pill";
import BookmarkButton from "./BookmarkButton";
import { MapPinIcon, BuildingIcon, LaptopIcon } from "./icons";

// Deterministic tinted logo tile per company (external logos are CSP-blocked,
// so we render a colored monogram instead).
const TILE_COLORS = [
  "bg-red-50 text-red-600",
  "bg-orange-50 text-orange-600",
  "bg-amber-50 text-amber-600",
  "bg-emerald-50 text-emerald-600",
  "bg-sky-50 text-sky-600",
  "bg-indigo-50 text-indigo-600",
  "bg-violet-50 text-violet-600",
  "bg-rose-50 text-rose-600",
];

function tileColor(name: string): string {
  let hash = 0;
  for (let i = 0; i < name.length; i++) hash = (hash * 31 + name.charCodeAt(i)) >>> 0;
  return TILE_COLORS[hash % TILE_COLORS.length];
}

function formatDate(epochSeconds: number): string {
  if (!epochSeconds) return "Date unknown";
  return new Date(epochSeconds * 1000).toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function locationLabel(locations: string[]): string {
  const [first, ...rest] = locations;
  if (!first) return "Location N/A";
  return rest.length ? `${first} +${rest.length} more` : first;
}

function workModel(locations: string[]): { label: string; icon: ReactNode } {
  const joined = locations.join(" ").toLowerCase();
  if (joined.includes("remote")) return { label: "Remote", icon: <LaptopIcon /> };
  if (joined.includes("hybrid")) return { label: "Hybrid", icon: <BuildingIcon /> };
  return { label: "In Person", icon: <BuildingIcon /> };
}

interface JobCardProps {
  job: Job;
}

export default function JobCard({ job }: JobCardProps) {
  const initial = (job.company_name || "?").charAt(0).toUpperCase();
  const seasonLabel = job.season && job.season !== "N/A" ? job.season : formatDate(job.date_posted);
  const wm = workModel(job.locations);

  return (
    <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-5 mb-4 transition-colors hover:bg-slate-50 hover:border-gray-300">
      {/* Top row: logo + company (left), bookmark (right) */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div
            className={`rounded-xl w-11 h-11 flex items-center justify-center font-bold text-lg ${tileColor(
              job.company_name
            )}`}
          >
            {initial}
          </div>
          {job.company_url ? (
            <a
              href={job.company_url}
              target="_blank"
              rel="noreferrer"
              className="text-gray-500 font-medium hover:text-gray-700"
            >
              {job.company_name}
            </a>
          ) : (
            <span className="text-gray-500 font-medium">{job.company_name}</span>
          )}
        </div>
        <BookmarkButton jobId={job.id} />
      </div>

      {/* Middle row: title */}
      <h2 className="mt-3">
        <a
          href={job.url}
          target="_blank"
          rel="noreferrer"
          className="text-xl font-bold text-gray-900 hover:underline"
        >
          {job.title}
        </a>
      </h2>

      {/* Bottom row: pills */}
      <div className="flex flex-wrap gap-2 mt-4">
        <Pill>{seasonLabel}</Pill>
        <Pill
          icon={<MapPinIcon />}
          title={job.locations.length > 1 ? job.locations.join(", ") : undefined}
        >
          {locationLabel(job.locations)}
        </Pill>
        <Pill icon={wm.icon}>{wm.label}</Pill>
      </div>
    </div>
  );
}
