/**
 * Artifact viewer component
 */

import { useQuery } from '@tanstack/react-query'
import { Download, ExternalLink, FileText, Image, File } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { artifactsApi } from '@/api/client'
import { formatBytes, truncateHash } from '@/lib/utils'
import { format } from 'date-fns'

interface ArtifactViewerProps {
  sha256: string
}

export function ArtifactViewer({ sha256 }: ArtifactViewerProps) {
  const { data: artifact, isLoading, error } = useQuery({
    queryKey: ['artifact', sha256],
    queryFn: () => artifactsApi.get(sha256),
  })

  const { data: urlData } = useQuery({
    queryKey: ['artifact-url', sha256],
    queryFn: () => artifactsApi.getContentUrl(sha256),
    enabled: !!artifact,
  })

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-muted-foreground">Loading artifact...</div>
      </div>
    )
  }

  if (error || !artifact) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-red-500">Failed to load artifact</div>
      </div>
    )
  }

  const getIcon = () => {
    if (artifact.media_type.startsWith('image/')) {
      return <Image className="h-12 w-12 text-muted-foreground" />
    }
    if (artifact.media_type.startsWith('text/') || artifact.media_type === 'application/json') {
      return <FileText className="h-12 w-12 text-muted-foreground" />
    }
    return <File className="h-12 w-12 text-muted-foreground" />
  }

  const isPreviewable =
    artifact.media_type.startsWith('image/') ||
    artifact.media_type.startsWith('text/') ||
    artifact.media_type === 'application/json' ||
    artifact.media_type === 'application/pdf'

  return (
    <div className="h-full p-6">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="flex items-start gap-4 mb-6">
          {getIcon()}
          <div className="flex-1">
            <h1 className="text-xl font-semibold">
              {artifact.filename || 'Unnamed Artifact'}
            </h1>
            <p
              className="text-sm text-muted-foreground font-mono mt-1"
              title={artifact.sha256}
            >
              {truncateHash(artifact.sha256, 16)}
            </p>
          </div>
          <div className="flex gap-2">
            {urlData && (
              <>
                <Button variant="outline" size="sm" asChild>
                  <a href={urlData.url} download>
                    <Download className="h-4 w-4 mr-2" />
                    Download
                  </a>
                </Button>
                <Button variant="outline" size="sm" asChild>
                  <a href={urlData.url} target="_blank" rel="noopener noreferrer">
                    <ExternalLink className="h-4 w-4 mr-2" />
                    Open
                  </a>
                </Button>
              </>
            )}
          </div>
        </div>

        <Separator className="my-4" />

        {/* Metadata */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="space-y-1">
            <p className="text-sm text-muted-foreground">Media Type</p>
            <p className="text-sm font-medium">{artifact.media_type}</p>
          </div>
          <div className="space-y-1">
            <p className="text-sm text-muted-foreground">Size</p>
            <p className="text-sm font-medium">{formatBytes(artifact.size_bytes)}</p>
          </div>
          <div className="space-y-1">
            <p className="text-sm text-muted-foreground">Created</p>
            <p className="text-sm font-medium">
              {format(new Date(artifact.created_at), 'PPpp')}
            </p>
          </div>
          <div className="space-y-1">
            <p className="text-sm text-muted-foreground">References</p>
            <p className="text-sm font-medium">{artifact.reference_count}</p>
          </div>
        </div>

        <Separator className="my-4" />

        {/* Preview */}
        {isPreviewable && urlData && (
          <div className="mt-6">
            <h2 className="text-sm font-semibold mb-3">Preview</h2>
            {artifact.media_type.startsWith('image/') ? (
              <div className="border rounded-lg p-4 bg-muted/50">
                <img
                  src={urlData.url}
                  alt={artifact.filename || 'Artifact preview'}
                  className="max-w-full h-auto rounded"
                />
              </div>
            ) : artifact.media_type === 'application/pdf' ? (
              <div className="border rounded-lg overflow-hidden" style={{ height: '600px' }}>
                <iframe
                  src={urlData.url}
                  className="w-full h-full"
                  title="PDF Preview"
                />
              </div>
            ) : (
              <div className="border rounded-lg p-4 bg-muted/50">
                <p className="text-sm text-muted-foreground">
                  Text preview not yet implemented
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
