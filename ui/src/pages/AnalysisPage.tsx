import { ModulePlaceholder } from '@/pages/ModulePlaceholder'

export function AnalysisPage() {
  return (
    <ModulePlaceholder
      title="Analysis Intelligence"
      tagline="Repeatable analysis that turns sources into structured outputs: tables, entities, relationships, and evidence-linked claims."
      status="next"
      bullets={[
        'DAG-style workflows that emit artifacts (tables/graphs/JSON) with provenance',
        'Entity/relationship extraction aligned to industry ontologies',
        'Comparisons and validations (IC memo vs model vs legal agreements)',
        'Levels of care: “quick read” vs “investment-grade” workflows',
      ]}
    />
  )
}

