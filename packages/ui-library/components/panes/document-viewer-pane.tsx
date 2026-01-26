import { useState, useCallback, useMemo } from 'react';
import {
  ZoomIn,
  ZoomOut,
  RotateCw,
  ChevronLeft,
  ChevronRight,
  Download,
  Highlighter,
  MessageSquare,
  Link2,
  Maximize2,
  Search,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { DocumentSkeleton } from '@/components/async/loading-states';
import { AsyncBoundary } from '@/components/async/suspense-wrapper';
import type { DocIRDocument, DocIRBlock, DocIRHighlight, EvidenceSpan } from '@/types';

interface DocumentViewerPaneProps {
  paneId: string;
}

// Mock DocIR document
const MOCK_DOCUMENT: DocIRDocument = {
  id: 'doc-1',
  sourceArtifactId: 'art-1',
  source: {
    filename: 'compliance-report-2024.pdf',
    mimeType: 'application/pdf',
    sizeBytes: 2450000,
    contentHash: 'sha256:abc123',
    pageCount: 3,
  },
  metadata: {
    title: 'Annual Compliance Report 2024',
    author: 'Compliance Team',
    createdAt: '2024-01-15T10:00:00Z',
    language: 'en',
    customFields: {},
  },
  pages: [
    {
      pageNumber: 1,
      dimensions: { width: 612, height: 792, unit: 'pt' },
      blocks: [
        { id: 'b1', type: 'heading', content: 'Annual Compliance Report 2024', attributes: { level: 1 } },
        { id: 'b2', type: 'paragraph', content: 'This document outlines the compliance requirements and controls for the fiscal year 2024.', attributes: {} },
        { id: 'b3', type: 'heading', content: '1. Data Protection Requirements', attributes: { level: 2 } },
        { id: 'b4', type: 'paragraph', content: 'Under GDPR Article 5, personal data must be processed lawfully, fairly, and in a transparent manner in relation to the data subject.', attributes: {} },
        { id: 'b5', type: 'list', content: '', children: [
          { id: 'b5a', type: 'list_item', content: 'Data minimization principles apply to all processing activities', attributes: {} },
          { id: 'b5b', type: 'list_item', content: 'Purpose limitation must be documented and enforced', attributes: {} },
          { id: 'b5c', type: 'list_item', content: 'Storage limitation policies must be implemented', attributes: {} },
        ], attributes: { listType: 'unordered' } },
      ],
    },
    {
      pageNumber: 2,
      dimensions: { width: 612, height: 792, unit: 'pt' },
      blocks: [
        { id: 'b6', type: 'heading', content: '2. Financial Reporting Controls', attributes: { level: 2 } },
        { id: 'b7', type: 'paragraph', content: 'SOX compliance requires internal controls over financial reporting. CEO and CFO certification is mandated.', attributes: {} },
        { id: 'b8', type: 'table', content: '', table: {
          rowCount: 3,
          columnCount: 3,
          cells: [
            { row: 0, col: 0, rowSpan: 1, colSpan: 1, content: 'Control', type: 'header' },
            { row: 0, col: 1, rowSpan: 1, colSpan: 1, content: 'Owner', type: 'header' },
            { row: 0, col: 2, rowSpan: 1, colSpan: 1, content: 'Status', type: 'header' },
            { row: 1, col: 0, rowSpan: 1, colSpan: 1, content: 'Revenue Recognition', type: 'data' },
            { row: 1, col: 1, rowSpan: 1, colSpan: 1, content: 'CFO', type: 'data' },
            { row: 1, col: 2, rowSpan: 1, colSpan: 1, content: 'Compliant', type: 'data' },
            { row: 2, col: 0, rowSpan: 1, colSpan: 1, content: 'Expense Approval', type: 'data' },
            { row: 2, col: 1, rowSpan: 1, colSpan: 1, content: 'Controller', type: 'data' },
            { row: 2, col: 2, rowSpan: 1, colSpan: 1, content: 'Compliant', type: 'data' },
          ],
        }, attributes: {} },
      ],
    },
    {
      pageNumber: 3,
      dimensions: { width: 612, height: 792, unit: 'pt' },
      blocks: [
        { id: 'b9', type: 'heading', content: '3. Security Controls (ISO 27001)', attributes: { level: 2 } },
        { id: 'b10', type: 'paragraph', content: 'An Information Security Management System (ISMS) is required. Risk assessment procedures must be documented and regularly reviewed.', attributes: {} },
        { id: 'b11', type: 'paragraph', content: 'All security incidents must be reported within 24 hours of detection.', attributes: {} },
      ],
    },
  ],
  extraction: {
    tool: 'docling',
    toolVersion: '1.2.0',
    extractedAt: new Date().toISOString(),
    configHash: 'abc123',
    quality: {
      overallConfidence: 0.95,
      textExtractionQuality: 'high',
      structureDetectionQuality: 'high',
      tableExtractionQuality: 'high',
      ocrUsed: false,
    },
  },
};

// Mock highlights/evidence
const MOCK_HIGHLIGHTS: DocIRHighlight[] = [
  {
    anchor: { documentId: 'doc-1', pageNumber: 1, blockId: 'b4', spanStart: 0, spanEnd: 45 },
    color: 'hsl(var(--evidence))',
    label: 'GDPR Requirement',
    linkedClaimId: 'claim-1',
  },
  {
    anchor: { documentId: 'doc-1', pageNumber: 2, blockId: 'b7', spanStart: 0, spanEnd: 35 },
    color: 'hsl(var(--claim))',
    label: 'SOX Control',
    linkedClaimId: 'claim-2',
  },
];

export function DocumentViewerPane({ paneId }: DocumentViewerPaneProps) {
  const [currentPage, setCurrentPage] = useState(1);
  const [zoom, setZoom] = useState(100);
  const [showOutline, setShowOutline] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedHighlight, setSelectedHighlight] = useState<string | null>(null);

  const document = MOCK_DOCUMENT;
  const totalPages = document.pages.length;

  const currentPageData = useMemo(
    () => document.pages.find((p) => p.pageNumber === currentPage),
    [document, currentPage]
  );

  const pageHighlights = useMemo(
    () => MOCK_HIGHLIGHTS.filter((h) => h.anchor.pageNumber === currentPage),
    [currentPage]
  );

  const handlePrevPage = useCallback(() => {
    setCurrentPage((prev) => Math.max(1, prev - 1));
  }, []);

  const handleNextPage = useCallback(() => {
    setCurrentPage((prev) => Math.min(totalPages, prev + 1));
  }, [totalPages]);

  const handleZoomIn = useCallback(() => {
    setZoom((prev) => Math.min(200, prev + 25));
  }, []);

  const handleZoomOut = useCallback(() => {
    setZoom((prev) => Math.max(50, prev - 25));
  }, []);

  return (
    <div className="h-full flex flex-col">
      {/* Toolbar */}
      <div className="h-10 border-b flex items-center justify-between px-2">
        <div className="flex items-center gap-1">
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon-sm" onClick={handleZoomOut}>
                <ZoomOut className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>Zoom out</TooltipContent>
          </Tooltip>
          <span className="text-xs w-12 text-center">{zoom}%</span>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon-sm" onClick={handleZoomIn}>
                <ZoomIn className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>Zoom in</TooltipContent>
          </Tooltip>

          <Separator orientation="vertical" className="h-5 mx-2" />

          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon-sm" onClick={handlePrevPage} disabled={currentPage === 1}>
                <ChevronLeft className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>Previous page</TooltipContent>
          </Tooltip>
          <span className="text-xs w-16 text-center">
            {currentPage} / {totalPages}
          </span>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon-sm" onClick={handleNextPage} disabled={currentPage === totalPages}>
                <ChevronRight className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>Next page</TooltipContent>
          </Tooltip>
        </div>

        <div className="flex items-center gap-1">
          <div className="relative">
            <Search className="absolute left-2 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" />
            <Input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search..."
              className="h-7 w-40 pl-7 text-xs"
            />
          </div>

          <Separator orientation="vertical" className="h-5 mx-2" />

          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon-sm">
                <Highlighter className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>Highlight selection</TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon-sm">
                <MessageSquare className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>Add comment</TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon-sm">
                <Link2 className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>Link to claim</TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon-sm">
                <Download className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>Download</TooltipContent>
          </Tooltip>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Outline sidebar */}
        {showOutline && (
          <div className="w-56 border-r">
            <div className="p-2 border-b">
              <h3 className="text-xs font-medium text-muted-foreground">Outline</h3>
            </div>
            <ScrollArea className="h-[calc(100%-36px)]">
              <div className="p-2 space-y-1">
                {document.pages.flatMap((page) =>
                  page.blocks
                    .filter((b) => b.type === 'heading')
                    .map((block) => (
                      <button
                        key={block.id}
                        className={cn(
                          'w-full text-left px-2 py-1 rounded text-xs hover:bg-muted truncate',
                          block.attributes.level === 1 ? 'font-medium' : 'pl-4 text-muted-foreground'
                        )}
                        onClick={() => setCurrentPage(page.pageNumber)}
                      >
                        {block.content}
                      </button>
                    ))
                )}
              </div>
            </ScrollArea>
          </div>
        )}

        {/* Document view */}
        <div className="flex-1 overflow-auto bg-muted/30">
          <AsyncBoundary loadingFallback={<DocumentSkeleton />}>
            <div
              className="p-8 mx-auto"
              style={{
                width: `${(currentPageData?.dimensions.width || 612) * (zoom / 100) + 64}px`,
              }}
            >
              <div
                className="bg-white dark:bg-zinc-900 shadow-lg rounded-sm p-8"
                style={{
                  transform: `scale(${zoom / 100})`,
                  transformOrigin: 'top left',
                  width: currentPageData?.dimensions.width,
                }}
              >
                {currentPageData?.blocks.map((block) => (
                  <DocumentBlock
                    key={block.id}
                    block={block}
                    highlights={pageHighlights.filter((h) => h.anchor.blockId === block.id)}
                    selectedHighlight={selectedHighlight}
                    onHighlightSelect={setSelectedHighlight}
                  />
                ))}
              </div>
            </div>
          </AsyncBoundary>
        </div>

        {/* Highlights panel */}
        {pageHighlights.length > 0 && (
          <div className="w-64 border-l">
            <div className="p-2 border-b">
              <h3 className="text-xs font-medium text-muted-foreground">
                Evidence ({pageHighlights.length})
              </h3>
            </div>
            <ScrollArea className="h-[calc(100%-36px)]">
              <div className="p-2 space-y-2">
                {pageHighlights.map((highlight) => (
                  <button
                    key={highlight.anchor.blockId}
                    className={cn(
                      'w-full text-left p-2 rounded border text-xs',
                      selectedHighlight === highlight.anchor.blockId
                        ? 'border-primary bg-primary/5'
                        : 'hover:bg-muted'
                    )}
                    onClick={() => setSelectedHighlight(highlight.anchor.blockId || null)}
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <div
                        className="w-2 h-2 rounded-full"
                        style={{ backgroundColor: highlight.color }}
                      />
                      <span className="font-medium">{highlight.label}</span>
                    </div>
                    {highlight.linkedClaimId && (
                      <Badge variant="claim" className="text-xs">
                        Linked claim
                      </Badge>
                    )}
                  </button>
                ))}
              </div>
            </ScrollArea>
          </div>
        )}
      </div>

      {/* Status bar */}
      <div className="h-6 border-t px-3 flex items-center justify-between text-xs text-muted-foreground">
        <span>{document.source.filename}</span>
        <span>Quality: {Math.round(document.extraction.quality.overallConfidence * 100)}%</span>
      </div>
    </div>
  );
}

function DocumentBlock({
  block,
  highlights,
  selectedHighlight,
  onHighlightSelect,
}: {
  block: DocIRBlock;
  highlights: DocIRHighlight[];
  selectedHighlight: string | null;
  onHighlightSelect: (id: string | null) => void;
}) {
  const hasHighlight = highlights.length > 0;
  const isSelected = block.id === selectedHighlight;
  const highlight = highlights[0];

  const blockStyles = cn(
    'relative',
    hasHighlight && 'cursor-pointer',
    isSelected && 'ring-2 ring-primary ring-offset-2'
  );

  const highlightStyles = hasHighlight
    ? {
        backgroundColor: `${highlight?.color}20`,
        borderLeft: `3px solid ${highlight?.color}`,
        paddingLeft: '8px',
        marginLeft: '-11px',
      }
    : {};

  switch (block.type) {
    case 'heading':
      const HeadingTag = `h${block.attributes.level || 1}` as keyof JSX.IntrinsicElements;
      const headingClasses = {
        1: 'text-2xl font-bold mb-4',
        2: 'text-xl font-semibold mb-3 mt-6',
        3: 'text-lg font-medium mb-2 mt-4',
      }[(block.attributes.level as number) || 1];
      return (
        <HeadingTag
          className={cn(headingClasses, blockStyles)}
          style={highlightStyles}
          onClick={() => hasHighlight && onHighlightSelect(isSelected ? null : block.id)}
        >
          {block.content}
        </HeadingTag>
      );

    case 'paragraph':
      return (
        <p
          className={cn('mb-3 text-sm leading-relaxed', blockStyles)}
          style={highlightStyles}
          onClick={() => hasHighlight && onHighlightSelect(isSelected ? null : block.id)}
        >
          {block.content}
        </p>
      );

    case 'list':
      const ListTag = block.attributes.listType === 'ordered' ? 'ol' : 'ul';
      return (
        <ListTag className={cn('mb-3 pl-5', block.attributes.listType === 'ordered' ? 'list-decimal' : 'list-disc')}>
          {block.children?.map((child) => (
            <li key={child.id} className="text-sm mb-1">
              {child.content}
            </li>
          ))}
        </ListTag>
      );

    case 'table':
      if (!block.table) return null;
      return (
        <div className="mb-4 overflow-x-auto">
          <table className="w-full border-collapse text-sm">
            <tbody>
              {Array.from({ length: block.table.rowCount }).map((_, rowIndex) => (
                <tr key={rowIndex}>
                  {block.table!.cells
                    .filter((cell) => cell.row === rowIndex)
                    .map((cell) => {
                      const CellTag = cell.type === 'header' ? 'th' : 'td';
                      return (
                        <CellTag
                          key={`${cell.row}-${cell.col}`}
                          rowSpan={cell.rowSpan}
                          colSpan={cell.colSpan}
                          className={cn(
                            'border px-3 py-2',
                            cell.type === 'header' ? 'bg-muted font-medium' : ''
                          )}
                        >
                          {cell.content}
                        </CellTag>
                      );
                    })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );

    default:
      return (
        <div className={cn('mb-3 text-sm', blockStyles)} style={highlightStyles}>
          {block.content}
        </div>
      );
  }
}
