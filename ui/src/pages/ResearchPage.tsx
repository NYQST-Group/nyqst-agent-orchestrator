import { ModulePlaceholder } from '@/pages/ModulePlaceholder'

export function ResearchPage() {
  return (
    <ModulePlaceholder
      title="Research Intelligence"
      tagline="Bring in sources (web, data rooms, emails, docs), capture provenance, and turn messy inputs into a governed source bundle."
      status="next"
      bullets={[
        'Source capture: URLs, uploads, connectors (Slack/Monday/HubSpot/Jira)',
        'Harvest + normalize into DocIR (swap Docling/Unstructured safely)',
        'Curate source bundles (pointer → manifest → artifacts)',
        'Research runs with a visible step trace (what happened, when, and why)',
      ]}
    />
  )
}

