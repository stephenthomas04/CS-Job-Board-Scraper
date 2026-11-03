import { useEffect, useState } from "react";
import { BookmarkIcon } from "./icons";

const STORAGE_KEY = "csjobdashboard:bookmarks";

function readBookmarks(): Record<string, boolean> {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
  } catch {
    return {};
  }
}

function writeBookmark(id: string, on: boolean) {
  const all = readBookmarks();
  if (on) {
    all[id] = true;
  } else {
    delete all[id];
  }
  localStorage.setItem(STORAGE_KEY, JSON.stringify(all));
}

interface BookmarkButtonProps {
  jobId: string;
}

export default function BookmarkButton({ jobId }: BookmarkButtonProps) {
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    setSaved(Boolean(readBookmarks()[jobId]));
  }, [jobId]);

  function toggle() {
    setSaved((prev) => {
      const next = !prev;
      writeBookmark(jobId, next);
      return next;
    });
  }

  return (
    <button
      type="button"
      onClick={toggle}
      aria-pressed={saved}
      aria-label={saved ? "Remove bookmark" : "Add bookmark"}
      title={saved ? "Bookmarked" : "Bookmark this job"}
      className={`transition-colors ${
        saved ? "text-gray-900" : "text-gray-300 hover:text-gray-500"
      }`}
    >
      <BookmarkIcon filled={saved} />
    </button>
  );
}
