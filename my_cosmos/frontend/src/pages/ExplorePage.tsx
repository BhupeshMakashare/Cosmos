import { useEffect, useState } from "react";
import type { Paper } from "../types";

export function ExplorePage() {
  // null = "not loaded yet"
  const [papers, setPapers] = useState<Paper[] | null>(null);

  useEffect(() => {
    fetch("/data/papers.json")
      .then((response) => response.json())
      .then((data: Paper[]) => setPapers(data));
  }, []);

  return (
    <section className="container-cosmos py-20">
      <p className="eyebrow">Space Research Intelligence</p>
      <h1 className="mt-3 text-4xl font-bold sm:text-6xl">
        Explore humanity's knowledge <span className="text-violet-500">beyond Earth.</span>
      </h1>
      {papers === null ? (
        <p className="mt-6 text-navy-500">Loading papers…</p>
      ) : (
        <div className="glass mt-8 max-w-xl p-6">
          <p className="text-2xl font-semibold">{papers.length.toLocaleString()} papers loaded</p>
          <p className="mt-2 text-sm text-navy-500">First paper: {papers[0].title}</p>
          <p className="mt-1 text-sm text-navy-500">Synthetic demo data: {papers[0].is_synthetic ? "yes" : "no"}</p>
        </div>
      )}
    </section>
  );
}
