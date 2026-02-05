# Oracle Cloud Always Free Setup

## Why Oracle
- Only cloud with always-free VMs (4 OCPU, 24 GB ARM) + managed converged database
- Autonomous DB does relational + vector + graph + JSON in ONE database, ONE query
- Replaces PostgreSQL + OpenSearch + Neo4j + Qdrant = 0 GB RAM for self-hosted DBs
- 10 TB/month outbound, 150 secrets, 1M notifications, 10 GB logging — all free

## Free Tier Inventory
- **Compute**: 4 ARM Ampere A1 OCPUs, 24 GB RAM (up to 4 VMs) + 2 AMD VMs (1/8 OCPU, 1 GB each)
- **Autonomous DB**: 2 instances, 1 OCPU + 20 GB each (converged: SQL + Vector + Graph + JSON + Text)
- **Storage**: 200 GB block/boot + 20 GB object storage
- **Networking**: 2 VCNs, 1 LB (10 Mbps), 10 TB outbound, 50 IPSec VPN
- **Security**: 150 Vault secrets, 20 HSM keys
- **Messaging**: 1M HTTPS notifications/month, Events Service (free)
- **Observability**: 10 GB logging, 500M monitoring points, 1K APM traces/hour
- **Containers**: OCIR ~5 GB, OKE free control plane
- **NOT free**: Streaming/Kafka, Queue, Container Instances, OCI Functions

## Key Risks
1. ARM capacity shortages — hard to provision, use retry scripts
2. Idle VM reclamation — CPU <20% for 7 days → deleted. Run keepalive cron
3. ADB concurrency — 3-6 concurrent users via HTTP. Mitigate with Redis caching + ORDS pooling
4. 50 Mbps bandwidth cap — fine for MCP JSON, use Object Storage PARs for large files
5. No SLA — free tier has no guarantees
6. No manual backup — weekly Data Pump exports as workaround

## Detailed Plans
See `/Users/markforster/NYQST-MCP/research/cloud-mcp-infrastructure/oracle-plan/`
