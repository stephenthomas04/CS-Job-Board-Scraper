import { useEffect, useMemo, useState } from "react";
import type { Job } from "../types";
import JobCard from "./JobCard";

// The converted dataset has ~15k rows; rendering every card at once is slow, so
// cap the number of cards in the DOM and let search narrow things down.
const RENDER_LIMIT = 100;

export default function JobList() {
  const [jobs, setJobs] = useState<Job[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState("");

  useEffect(() => {
    let cancelled = false;
    fetch("/listings.json")
      .then((res) => {
        if (!res.ok) throw new Error(`Failed to load listings (${res.status})`);
        return res.json();
      })
      .then((data: Job[]) => {
        if (!cancelled) setJobs(data.filter((j) => j.is_visible));
      })
      .catch((err) => {
        if (!cancelled) setError(err.message);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const filtered = useMemo(() => {
    if (!jobs) return [];
    const q = query.trim().toLowerCase();
    if (!q) return jobs;
    return jobs.filter(
      (j) =>
        j.title.toLowerCase().includes(q) ||
        j.company_name.toLowerCase().includes(q)
    );
  }, [jobs, query]);

  if (error) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 text-red-700 p-5">
        Couldn’t load listings: {error}
      </div>
    );
  }

  if (jobs === null) {
    return <div className="text-gray-500 p-5 text-center">Loading listings…</div>;
  }

  const visible = filtered.slice(0, RENDER_LIMIT);

  return (
    <div>
      <input
        type="search"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search by title or company…"
        className="w-full rounded-xl border border-gray-200 bg-white px-4 py-2 mb-4 shadow-sm focus:outline-none focus:ring-2 focus:ring-gray-300"
      />

      <p className="text-sm text-gray-500 mb-4">
        Showing {visible.length} of {filtered.length.toLocaleString()} listings
      </p>

      {filtered.length === 0 ? (
        <div className="text-gray-500 p-5 text-center">No listings match your search.</div>
      ) : (
        visible.map((job) => <JobCard key={`${job.source}:${job.id}`} job={job} />)
      )}
    </div>
  );
}
