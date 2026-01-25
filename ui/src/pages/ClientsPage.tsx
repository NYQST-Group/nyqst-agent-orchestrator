import { ModulePlaceholder } from '@/pages/ModulePlaceholder'

export function ClientsPage() {
  return (
    <ModulePlaceholder
      title="Client Intelligence"
      tagline="Lightweight CRM objects that link back to analysis: who the client is, what’s been delivered, and the evidence behind it."
      status="later"
      bullets={[
        'Clients/accounts with linked projects, runs, and deliverables',
        'Client-specific corpora/knowledge bases with governance',
        'Connector-driven sync (treat external systems as sources of truth)',
        'Audit and retention policy per client/tenant',
      ]}
    />
  )
}

