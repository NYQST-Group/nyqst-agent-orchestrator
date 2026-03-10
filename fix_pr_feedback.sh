#!/usr/bin/env bash
set -eo pipefail

# 1. Regenerate yarn.lock correctly in the backstage workspace
cd backstage
yarn install --mode=update-lockfile
cd ..

# 2. Update GitHub Actions YAML to include ui-library types
sed -i '' "s|      - 'ui/src/types/\*\*'|      - 'ui/src/types/\*\*'\n      - 'packages/ui-library/types/\*\*'|" .github/workflows/backstage-schemas.yml

# 3. Update the fake workflow steps to fail until implemented
sed -i '' 's/# Mock step for M0: In the future, run datamodel-codegen checks here/exit 1 # TODO: Implement real datamodel-codegen checks/' .github/workflows/backstage-schemas.yml
sed -i '' 's/# Mock step for M0: Call Backstage API to ingest the latest catalog-info.yaml/exit 1 # TODO: Implement real Backstage API ingestion/' .github/workflows/backstage-schemas.yml

# 4. Fix catalog-info.yaml ownership
sed -i '' 's/owner: mark@nyqst.ai/owner: group:default\/guests/' backstage/catalog-info.yaml

# 5. Fix App.test.tsx process.env overwrite
sed -i '' 's/process.env = { ...originalEnv, APP_CONFIG: /process.env.APP_CONFIG = /' backstage/packages/app/src/App.test.tsx

# Note: The 'allow-all' permission policy and 'guest' auth provider in production are expected 
# for a brand new scaffold (Backstage generates them by default) and will be hardened in a later epic.
# We will leave those as they are but resolve the immediate broken states.

git add .
git commit -m "fix(infra): Address Copilot/Codex PR review feedback for Backstage scaffold"
