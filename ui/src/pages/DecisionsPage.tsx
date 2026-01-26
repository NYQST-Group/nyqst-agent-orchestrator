import { ModulePlaceholder } from '@/pages/ModulePlaceholder'

export function DecisionsPage() {
  return (
    <ModulePlaceholder
      title="Decision Intelligence"
      tagline="Make outputs trustworthy: confidence, recommendations, approvals, and a clear audit trail for skeptical stakeholders."
      status="later"
      bullets={[
        'Claims with confidence + “recommended next actions”',
        'Evidence spans and citations (why we believe this)',
        'Approvals and sign-offs (promotion gates)',
        'Diffs and degradation hooks when source bundles change',
      ]}
    />
  )
}

