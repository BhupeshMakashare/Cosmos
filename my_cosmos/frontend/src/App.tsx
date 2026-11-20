import { Chip, CosmicLoader, EmptyState, GlassCard, SectionHeader, StatCard } from "./components/ui";

export default function App() {
  return (
    <main className="container-cosmos space-y-12 py-16">
      <SectionHeader eyebrow="Design system" title="COSMOS components" description="Every page is built from these pieces." />

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <StatCard value={1500} label="Research papers" />
        <StatCard value={14} label="Countries" />
        <StatCard value={38} label="Research topics" />
        <StatCard value={84} label="Organizations" />
      </div>

      <div className="flex flex-wrap gap-2">
        <Chip>Computer Vision</Chip>
        <Chip tone="method">Deep Learning</Chip>
        <Chip tone="entity">Star Trackers</Chip>
        <Chip tone="signal">Emerging topic signal</Chip>
      </div>

      <GlassCard className="p-6">
        <p className="font-semibold">A glass card</p>
        <p className="mt-1 text-sm text-navy-500">Put anything inside.</p>
      </GlassCard>

      <GlassCard>
        <CosmicLoader label="Searching the research universe…" />
      </GlassCard>

      <GlassCard>
        <EmptyState title="No papers match these filters." hint="Try removing a filter." />
      </GlassCard>
    </main>
  );
}
