import { useState, useMemo } from 'react';
import {
  Shield,
  CheckCircle,
  Clock,
  AlertTriangle,
  ChevronRight,
  FileCheck,
  Users,
  History,
  MoreHorizontal,
  Eye,
  ThumbsUp,
  ThumbsDown,
  MessageSquare,
} from 'lucide-react';
import { cn, formatRelativeTime } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ListSkeleton } from '@/components/async/loading-states';
import { AsyncBoundary } from '@/components/async/suspense-wrapper';
import type { Corpus, Bundle, Decision, GovernanceLevel } from '@/types';

interface GovernancePaneProps {
  paneId: string;
}

// Mock data
const MOCK_CORPORA: Corpus[] = [
  {
    id: 'corpus-1',
    tenantId: 'tenant-1',
    name: 'GDPR Compliance Documentation',
    description: 'Official GDPR compliance documentation for Q4 2024',
    headPointerId: 'pointer-1',
    governanceProfile: {
      level: 'certified',
      requiredGates: ['schema_validation', 'coverage_check', 'legal_review'],
      approvalWorkflow: {
        stages: [
          { name: 'Technical Review', approverIds: ['user-1'], minApprovals: 1 },
          { name: 'Legal Review', approverIds: ['user-2', 'user-3'], minApprovals: 1 },
        ],
        requireAllApprovers: false,
      },
      recertScheduleDays: 90,
    },
    downstreamDependencies: [
      { dependentType: 'kb', dependentId: 'kb-1', dependencyType: 'source' },
    ],
    metadata: { version: 3, lastCertifiedAt: new Date(Date.now() - 7776000000).toISOString() },
    createdAt: new Date(Date.now() - 15552000000).toISOString(),
    updatedAt: new Date(Date.now() - 86400000).toISOString(),
  },
  {
    id: 'corpus-2',
    tenantId: 'tenant-1',
    name: 'Financial Controls Manual',
    description: 'SOX compliance controls and procedures',
    headPointerId: 'pointer-2',
    governanceProfile: {
      level: 'governed',
      requiredGates: ['schema_validation', 'audit_check'],
      recertScheduleDays: 180,
    },
    downstreamDependencies: [],
    metadata: { version: 5 },
    createdAt: new Date(Date.now() - 31104000000).toISOString(),
    updatedAt: new Date(Date.now() - 172800000).toISOString(),
  },
];

const MOCK_PENDING_APPROVALS: (Decision & { subjectName: string })[] = [
  {
    id: 'decision-1',
    tenantId: 'tenant-1',
    projectId: 'project-1',
    type: 'approval',
    context: 'corpus_promotion',
    subjectType: 'corpus',
    subjectId: 'corpus-3',
    subjectName: 'Q4 Risk Assessment Bundle',
    deciderId: '',
    outcome: 'approved',
    rationale: '',
    metadata: { requestedBy: 'user-1', stage: 'Technical Review' },
    createdAt: new Date(Date.now() - 3600000).toISOString(),
    updatedAt: new Date(Date.now() - 3600000).toISOString(),
  },
  {
    id: 'decision-2',
    tenantId: 'tenant-1',
    projectId: 'project-1',
    type: 'approval',
    context: 'claim_review',
    subjectType: 'claim',
    subjectId: 'claim-5',
    subjectName: 'Data Retention Policy Requirement',
    deciderId: '',
    outcome: 'approved',
    rationale: '',
    metadata: { confidence: 'high', evidenceCount: 3 },
    createdAt: new Date(Date.now() - 7200000).toISOString(),
    updatedAt: new Date(Date.now() - 7200000).toISOString(),
  },
];

const GOVERNANCE_LEVEL_CONFIG: Record<GovernanceLevel, { color: string; icon: React.ElementType }> = {
  standard: { color: 'bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-400', icon: Shield },
  governed: { color: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400', icon: FileCheck },
  certified: { color: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400', icon: CheckCircle },
};

export function GovernancePane({ paneId }: GovernancePaneProps) {
  const [activeTab, setActiveTab] = useState('overview');

  return (
    <div className="h-full flex flex-col">
      <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
        <div className="border-b px-4">
          <TabsList className="h-10">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="approvals">
              Pending Approvals
              {MOCK_PENDING_APPROVALS.length > 0 && (
                <Badge variant="destructive" className="ml-1.5 h-5 px-1.5">
                  {MOCK_PENDING_APPROVALS.length}
                </Badge>
              )}
            </TabsTrigger>
            <TabsTrigger value="corpora">Corpora</TabsTrigger>
            <TabsTrigger value="history">History</TabsTrigger>
          </TabsList>
        </div>

        <TabsContent value="overview" className="flex-1 overflow-hidden mt-0">
          <GovernanceOverview />
        </TabsContent>

        <TabsContent value="approvals" className="flex-1 overflow-hidden mt-0">
          <PendingApprovals approvals={MOCK_PENDING_APPROVALS} />
        </TabsContent>

        <TabsContent value="corpora" className="flex-1 overflow-hidden mt-0">
          <CorporaList corpora={MOCK_CORPORA} />
        </TabsContent>

        <TabsContent value="history" className="flex-1 overflow-hidden mt-0">
          <GovernanceHistory />
        </TabsContent>
      </Tabs>
    </div>
  );
}

function GovernanceOverview() {
  const stats = {
    totalCorpora: MOCK_CORPORA.length,
    certified: MOCK_CORPORA.filter((c) => c.governanceProfile.level === 'certified').length,
    pendingApprovals: MOCK_PENDING_APPROVALS.length,
    upcomingRecerts: 1,
  };

  return (
    <ScrollArea className="h-full">
      <div className="p-4 space-y-6">
        {/* Stats cards */}
        <div className="grid grid-cols-4 gap-4">
          <StatCard
            title="Total Corpora"
            value={stats.totalCorpora}
            icon={Shield}
            color="text-primary"
          />
          <StatCard
            title="Certified"
            value={stats.certified}
            icon={CheckCircle}
            color="text-green-500"
          />
          <StatCard
            title="Pending Approvals"
            value={stats.pendingApprovals}
            icon={Clock}
            color="text-yellow-500"
          />
          <StatCard
            title="Upcoming Recerts"
            value={stats.upcomingRecerts}
            icon={AlertTriangle}
            color="text-orange-500"
          />
        </div>

        {/* Recent activity */}
        <div>
          <h3 className="text-sm font-medium mb-3">Recent Activity</h3>
          <div className="space-y-2">
            {[
              { action: 'Corpus promoted', subject: 'GDPR Documentation v3', time: '2 hours ago', type: 'success' },
              { action: 'Approval requested', subject: 'Q4 Risk Assessment', time: '4 hours ago', type: 'pending' },
              { action: 'Gate failed', subject: 'Draft Policy Bundle', time: '1 day ago', type: 'error' },
            ].map((activity, i) => (
              <div key={i} className="flex items-center gap-3 p-2 rounded-md hover:bg-muted/50">
                <div
                  className={cn(
                    'w-2 h-2 rounded-full',
                    activity.type === 'success' && 'bg-green-500',
                    activity.type === 'pending' && 'bg-yellow-500',
                    activity.type === 'error' && 'bg-red-500'
                  )}
                />
                <div className="flex-1">
                  <span className="text-sm">{activity.action}: </span>
                  <span className="text-sm font-medium">{activity.subject}</span>
                </div>
                <span className="text-xs text-muted-foreground">{activity.time}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Governance policies */}
        <div>
          <h3 className="text-sm font-medium mb-3">Active Policies</h3>
          <div className="grid grid-cols-2 gap-3">
            {[
              { name: 'Data Retention', status: 'Active', scope: 'All corpora' },
              { name: 'Access Control', status: 'Active', scope: 'Certified only' },
              { name: 'Recertification', status: 'Active', scope: '90-day cycle' },
            ].map((policy, i) => (
              <div key={i} className="p-3 rounded-lg border">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium">{policy.name}</span>
                  <Badge variant="success" className="text-xs">
                    {policy.status}
                  </Badge>
                </div>
                <span className="text-xs text-muted-foreground">{policy.scope}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </ScrollArea>
  );
}

function StatCard({
  title,
  value,
  icon: Icon,
  color,
}: {
  title: string;
  value: number;
  icon: React.ElementType;
  color: string;
}) {
  return (
    <div className="p-4 rounded-lg border bg-card">
      <div className="flex items-center justify-between">
        <span className="text-2xl font-bold">{value}</span>
        <Icon className={cn('h-5 w-5', color)} />
      </div>
      <span className="text-xs text-muted-foreground">{title}</span>
    </div>
  );
}

function PendingApprovals({ approvals }: { approvals: (Decision & { subjectName: string })[] }) {
  return (
    <AsyncBoundary loadingFallback={<ListSkeleton />}>
      <ScrollArea className="h-full">
        <div className="p-4 space-y-3">
          {approvals.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <CheckCircle className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p>No pending approvals</p>
            </div>
          ) : (
            approvals.map((approval) => (
              <ApprovalCard key={approval.id} approval={approval} />
            ))
          )}
        </div>
      </ScrollArea>
    </AsyncBoundary>
  );
}

function ApprovalCard({ approval }: { approval: Decision & { subjectName: string } }) {
  return (
    <div className="p-4 rounded-lg border bg-card">
      <div className="flex items-start justify-between mb-2">
        <div>
          <h4 className="text-sm font-medium">{approval.subjectName}</h4>
          <div className="flex items-center gap-2 mt-1">
            <Badge variant="outline" className="text-xs">
              {approval.context.replace('_', ' ')}
            </Badge>
            <span className="text-xs text-muted-foreground">
              {formatRelativeTime(approval.createdAt)}
            </span>
          </div>
        </div>
        <Badge variant="warning" className="text-xs">
          Pending
        </Badge>
      </div>

      {approval.metadata.stage && (
        <p className="text-xs text-muted-foreground mb-3">
          Stage: {approval.metadata.stage as string}
        </p>
      )}

      <div className="flex items-center gap-2">
        <Button size="sm" variant="default" className="gap-1">
          <ThumbsUp className="h-3.5 w-3.5" />
          Approve
        </Button>
        <Button size="sm" variant="outline" className="gap-1">
          <ThumbsDown className="h-3.5 w-3.5" />
          Reject
        </Button>
        <Button size="sm" variant="ghost" className="gap-1">
          <Eye className="h-3.5 w-3.5" />
          Review
        </Button>
        <Button size="sm" variant="ghost" className="gap-1">
          <MessageSquare className="h-3.5 w-3.5" />
          Comment
        </Button>
      </div>
    </div>
  );
}

function CorporaList({ corpora }: { corpora: Corpus[] }) {
  return (
    <AsyncBoundary loadingFallback={<ListSkeleton />}>
      <ScrollArea className="h-full">
        <div className="p-4 space-y-2">
          {corpora.map((corpus) => {
            const levelConfig = GOVERNANCE_LEVEL_CONFIG[corpus.governanceProfile.level];
            const LevelIcon = levelConfig.icon;

            return (
              <div
                key={corpus.id}
                className="p-3 rounded-lg border bg-card hover:shadow-sm transition-shadow cursor-pointer"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <h4 className="text-sm font-medium truncate">{corpus.name}</h4>
                      <Badge className={cn('text-xs', levelConfig.color)}>
                        <LevelIcon className="h-3 w-3 mr-1" />
                        {corpus.governanceProfile.level}
                      </Badge>
                    </div>
                    {corpus.description && (
                      <p className="text-xs text-muted-foreground mt-1 truncate">
                        {corpus.description}
                      </p>
                    )}
                  </div>
                  <ChevronRight className="h-4 w-4 text-muted-foreground shrink-0" />
                </div>

                <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                  <span className="flex items-center gap-1">
                    <FileCheck className="h-3.5 w-3.5" />
                    {corpus.governanceProfile.requiredGates.length} gates
                  </span>
                  {corpus.governanceProfile.approvalWorkflow && (
                    <span className="flex items-center gap-1">
                      <Users className="h-3.5 w-3.5" />
                      {corpus.governanceProfile.approvalWorkflow.stages.length} stages
                    </span>
                  )}
                  <span className="flex items-center gap-1">
                    <History className="h-3.5 w-3.5" />
                    v{corpus.metadata.version as number}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </ScrollArea>
    </AsyncBoundary>
  );
}

function GovernanceHistory() {
  const historyItems = [
    { type: 'promotion', subject: 'GDPR Documentation', from: 'v2', to: 'v3', by: 'John Smith', at: '2 days ago' },
    { type: 'approval', subject: 'Financial Controls', decision: 'Approved', by: 'Jane Doe', at: '5 days ago' },
    { type: 'gate_pass', subject: 'Risk Assessment', gate: 'Schema Validation', at: '1 week ago' },
    { type: 'gate_fail', subject: 'Draft Policy', gate: 'Coverage Check', reason: 'Insufficient evidence', at: '1 week ago' },
  ];

  return (
    <ScrollArea className="h-full">
      <div className="p-4 space-y-3">
        {historyItems.map((item, i) => (
          <div key={i} className="flex gap-3 p-2">
            <div
              className={cn(
                'w-8 h-8 rounded-full flex items-center justify-center shrink-0',
                item.type === 'promotion' && 'bg-blue-100 text-blue-600',
                item.type === 'approval' && 'bg-green-100 text-green-600',
                item.type === 'gate_pass' && 'bg-green-100 text-green-600',
                item.type === 'gate_fail' && 'bg-red-100 text-red-600'
              )}
            >
              {item.type === 'promotion' && <History className="h-4 w-4" />}
              {item.type === 'approval' && <CheckCircle className="h-4 w-4" />}
              {item.type === 'gate_pass' && <FileCheck className="h-4 w-4" />}
              {item.type === 'gate_fail' && <AlertTriangle className="h-4 w-4" />}
            </div>
            <div className="flex-1">
              <p className="text-sm">
                <span className="font-medium">{item.subject}</span>
                {item.type === 'promotion' && ` promoted from ${item.from} to ${item.to}`}
                {item.type === 'approval' && ` ${item.decision.toLowerCase()}`}
                {item.type === 'gate_pass' && ` passed ${item.gate}`}
                {item.type === 'gate_fail' && ` failed ${item.gate}`}
              </p>
              <div className="flex items-center gap-2 text-xs text-muted-foreground mt-0.5">
                {item.by && <span>by {item.by}</span>}
                <span>{item.at}</span>
              </div>
              {item.reason && (
                <p className="text-xs text-destructive mt-1">{item.reason}</p>
              )}
            </div>
          </div>
        ))}
      </div>
    </ScrollArea>
  );
}
