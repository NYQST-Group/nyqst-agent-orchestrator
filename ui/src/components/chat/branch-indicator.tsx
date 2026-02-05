/**
 * Branch indicator showing sibling count and prev/next navigation.
 */

import { ChevronLeft, ChevronRight, GitBranch } from 'lucide-react'

import { Button } from '@/components/ui/button'

interface BranchIndicatorProps {
  siblingCount: number
  currentIndex: number
  onPrev: () => void
  onNext: () => void
}

export function BranchIndicator({
  siblingCount,
  currentIndex,
  onPrev,
  onNext,
}: BranchIndicatorProps) {
  if (siblingCount <= 1) return null

  return (
    <div className="flex items-center gap-1 text-xs text-muted-foreground">
      <GitBranch className="h-3 w-3" />
      <Button
        variant="ghost"
        size="icon"
        className="h-5 w-5"
        onClick={onPrev}
        disabled={currentIndex <= 0}
      >
        <ChevronLeft className="h-3 w-3" />
      </Button>
      <span>
        {currentIndex + 1}/{siblingCount}
      </span>
      <Button
        variant="ghost"
        size="icon"
        className="h-5 w-5"
        onClick={onNext}
        disabled={currentIndex >= siblingCount - 1}
      >
        <ChevronRight className="h-3 w-3" />
      </Button>
    </div>
  )
}
