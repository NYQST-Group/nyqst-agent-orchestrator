import { ModulePlaceholder } from '@/pages/ModulePlaceholder'

export function ProjectsPage() {
  return (
    <ModulePlaceholder
      title="Project Intelligence"
      tagline="Objectives and workstreams that organize runs and artifacts into a deliverable stakeholders can review and trust."
      status="later"
      bullets={[
        'Projects/objectives with pinned bundles and output artifacts',
        'Deliverable packs (export snapshots for clients)',
        'Work tracking + “what changed” timeline (pointer moves and diffs)',
        'Agent assistance that can update records with full traceability',
      ]}
    />
  )
}

