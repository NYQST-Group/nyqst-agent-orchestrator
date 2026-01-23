/**
 * Document Intermediate Representation (DocIR) types
 * Canonical representation for document processing (Section 9 of reference design)
 */

import type { UUID, Timestamp, ContentHash } from './core';

// ============================================================================
// DocIR Root Document
// ============================================================================

export interface DocIRDocument {
  /** Document unique identifier */
  id: UUID;
  /** Source artifact ID */
  sourceArtifactId: UUID;
  /** Source file information */
  source: DocIRSource;
  /** Document metadata */
  metadata: DocIRMetadata;
  /** Pages in the document */
  pages: DocIRPage[];
  /** Document-level table of contents */
  toc?: DocIRTocEntry[];
  /** Extraction provenance */
  extraction: DocIRExtraction;
}

export interface DocIRSource {
  filename: string;
  mimeType: string;
  sizeBytes: number;
  contentHash: ContentHash;
  pageCount: number;
}

export interface DocIRMetadata {
  title?: string;
  author?: string;
  subject?: string;
  keywords?: string[];
  createdAt?: Timestamp;
  modifiedAt?: Timestamp;
  producer?: string;
  language?: string;
  customFields: Record<string, unknown>;
}

export interface DocIRExtraction {
  tool: string;
  toolVersion: string;
  extractedAt: Timestamp;
  configHash: ContentHash;
  quality: DocIRQualityMetrics;
}

export interface DocIRQualityMetrics {
  overallConfidence: number;
  textExtractionQuality: 'high' | 'medium' | 'low';
  structureDetectionQuality: 'high' | 'medium' | 'low';
  tableExtractionQuality?: 'high' | 'medium' | 'low';
  ocrUsed: boolean;
  ocrConfidence?: number;
}

// ============================================================================
// Page Structure
// ============================================================================

export interface DocIRPage {
  pageNumber: number;
  /** Page dimensions in points (1/72 inch) */
  dimensions: DocIRDimensions;
  /** Blocks on this page */
  blocks: DocIRBlock[];
  /** Page-level metadata */
  metadata?: Record<string, unknown>;
}

export interface DocIRDimensions {
  width: number;
  height: number;
  unit: 'pt' | 'px' | 'mm';
}

// ============================================================================
// Block Types
// ============================================================================

export type DocIRBlockType =
  | 'heading'
  | 'paragraph'
  | 'list'
  | 'list_item'
  | 'table'
  | 'figure'
  | 'caption'
  | 'header'
  | 'footer'
  | 'footnote'
  | 'code'
  | 'quote'
  | 'page_break'
  | 'unknown';

export interface DocIRBlock {
  /** Unique block identifier within the document */
  id: string;
  /** Block type */
  type: DocIRBlockType;
  /** Text content (for text blocks) */
  content?: string;
  /** Nested blocks (for containers like lists) */
  children?: DocIRBlock[];
  /** Table data (for table blocks) */
  table?: DocIRTable;
  /** Figure data (for figure blocks) */
  figure?: DocIRFigure;
  /** Text spans with formatting */
  spans?: DocIRSpan[];
  /** Layout geometry */
  geometry?: DocIRGeometry;
  /** Block-level attributes */
  attributes: DocIRBlockAttributes;
  /** Confidence score for this block */
  confidence?: number;
}

export interface DocIRBlockAttributes {
  level?: number; // For headings (1-6)
  listType?: 'ordered' | 'unordered';
  listLevel?: number;
  language?: string; // For code blocks
  alignment?: 'left' | 'center' | 'right' | 'justify';
  indentation?: number;
  customAttributes?: Record<string, unknown>;
}

// ============================================================================
// Text Spans
// ============================================================================

export interface DocIRSpan {
  /** Start offset within block content */
  startOffset: number;
  /** End offset within block content */
  endOffset: number;
  /** Text content of this span */
  text: string;
  /** Formatting applied to this span */
  formatting?: DocIRFormatting;
  /** Link target if this is a link */
  link?: DocIRLink;
  /** Entity annotation if detected */
  entity?: DocIREntity;
}

export interface DocIRFormatting {
  bold?: boolean;
  italic?: boolean;
  underline?: boolean;
  strikethrough?: boolean;
  superscript?: boolean;
  subscript?: boolean;
  fontFamily?: string;
  fontSize?: number;
  color?: string;
  backgroundColor?: string;
}

export interface DocIRLink {
  type: 'external' | 'internal' | 'anchor';
  target: string;
  title?: string;
}

export interface DocIREntity {
  type: string;
  value: string;
  confidence: number;
  metadata?: Record<string, unknown>;
}

// ============================================================================
// Layout Geometry
// ============================================================================

export interface DocIRGeometry {
  /** Bounding box */
  bbox: DocIRBoundingBox;
  /** Reading order index */
  readingOrder?: number;
  /** Column index if multi-column */
  columnIndex?: number;
}

export interface DocIRBoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

// ============================================================================
// Table Model
// ============================================================================

export interface DocIRTable {
  /** Number of rows */
  rowCount: number;
  /** Number of columns */
  columnCount: number;
  /** Table cells */
  cells: DocIRTableCell[];
  /** Table caption if present */
  caption?: string;
  /** Column headers if detected */
  headers?: DocIRTableHeader[];
  /** Table-level metadata */
  metadata?: Record<string, unknown>;
}

export interface DocIRTableCell {
  /** Row index (0-based) */
  row: number;
  /** Column index (0-based) */
  col: number;
  /** Row span */
  rowSpan: number;
  /** Column span */
  colSpan: number;
  /** Cell content */
  content: string;
  /** Content blocks within cell */
  blocks?: DocIRBlock[];
  /** Cell type */
  type: 'header' | 'data';
  /** Cell geometry */
  geometry?: DocIRGeometry;
}

export interface DocIRTableHeader {
  columnIndex: number;
  label: string;
  dataType?: 'text' | 'number' | 'date' | 'currency' | 'percentage';
}

// ============================================================================
// Figure Model
// ============================================================================

export interface DocIRFigure {
  /** Figure type */
  type: 'image' | 'chart' | 'diagram' | 'equation' | 'unknown';
  /** Image artifact reference if extracted */
  imageArtifactId?: UUID;
  /** Alt text or description */
  altText?: string;
  /** Caption if present */
  caption?: string;
  /** OCR text if applicable */
  ocrText?: string;
  /** Bounding box */
  geometry?: DocIRGeometry;
}

// ============================================================================
// Table of Contents
// ============================================================================

export interface DocIRTocEntry {
  title: string;
  level: number;
  pageNumber?: number;
  blockId?: string;
  children?: DocIRTocEntry[];
}

// ============================================================================
// Evidence Anchoring
// ============================================================================

export interface DocIRAnchor {
  documentId: UUID;
  pageNumber: number;
  blockId: string;
  spanStart?: number;
  spanEnd?: number;
}

export interface DocIRHighlight {
  anchor: DocIRAnchor;
  color: string;
  label?: string;
  notes?: string;
  linkedClaimId?: UUID;
}

// ============================================================================
// DocIR Diff
// ============================================================================

export interface DocIRDiff {
  documentId: UUID;
  previousVersion: UUID;
  currentVersion: UUID;
  changes: DocIRChange[];
  stats: DocIRDiffStats;
}

export type DocIRChangeType = 'added' | 'removed' | 'modified' | 'moved';

export interface DocIRChange {
  type: DocIRChangeType;
  blockType: DocIRBlockType;
  blockId?: string;
  previousBlockId?: string;
  previousContent?: string;
  currentContent?: string;
  pageNumber?: number;
  previousPageNumber?: number;
}

export interface DocIRDiffStats {
  blocksAdded: number;
  blocksRemoved: number;
  blocksModified: number;
  blocksMoved: number;
  pagesAdded: number;
  pagesRemoved: number;
}
