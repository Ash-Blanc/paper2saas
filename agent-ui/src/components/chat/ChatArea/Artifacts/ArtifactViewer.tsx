'use client'

import { Artifact } from '@/types/artifacts'
import { FC, useState } from 'react'
import { Button } from '@/components/ui/button'
import Icon from '@/components/ui/icon'
import MarkdownRenderer from '@/components/ui/typography/MarkdownRenderer'
import { cn } from '@/lib/utils'
import { toast } from 'sonner'

interface ArtifactViewerProps {
  artifact: Artifact | null
  onClose: () => void
}

const ArtifactViewer: FC<ArtifactViewerProps> = ({ artifact, onClose }) => {
  const [copySuccess, setCopySuccess] = useState(false)

  if (!artifact) return null

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(artifact.content)
      setCopySuccess(true)
      toast.success('Copied to clipboard')
      setTimeout(() => setCopySuccess(false), 2000)
    } catch {
      toast.error('Failed to copy')
    }
  }

  const handleDownload = () => {
    const blob = new Blob([artifact.content], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    const extension = getFileExtension(artifact.type, artifact.language)
    a.download = `${artifact.title.replace(/[^a-z0-9]/gi, '_')}.${extension}`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    toast.success('Downloaded successfully')
  }

  const getFileExtension = (type: string, language?: string): string => {
    if (type === 'code' && language) return language
    if (type === 'markdown' || type === 'report') return 'md'
    if (type === 'json') return 'json'
    if (type === 'html') return 'html'
    return 'txt'
  }

  return (
    <div className="flex h-full flex-col bg-background">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-border/30 px-4 py-3">
        <div className="flex items-center gap-3">
          <div className="rounded-lg bg-primary/10 px-2 py-1">
            <span className="text-xs font-medium uppercase text-primary">
              {artifact.type}
            </span>
          </div>
          <h2 className="font-dmmono text-sm font-medium text-primary">
            {artifact.title}
          </h2>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="icon"
            onClick={handleCopy}
            className="h-8 w-8"
            title="Copy to clipboard"
          >
            {copySuccess ? (
              <Icon type="check" size="xs" />
            ) : (
              <Icon type="clipboard" size="xs" />
            )}
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={handleDownload}
            className="h-8 w-8"
            title="Download"
          >
            <Icon type="download" size="xs" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={onClose}
            className="h-8 w-8"
            title="Close"
          >
            <Icon type="x" size="xs" />
          </Button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        {artifact.type === 'code' ? (
          <pre className="rounded-lg bg-background-secondary p-4 text-sm">
            <code className={cn('font-dmmono', `language-${artifact.language}`)}>
              {artifact.content}
            </code>
          </pre>
        ) : artifact.type === 'json' ? (
          <pre className="rounded-lg bg-background-secondary p-4 text-sm">
            <code className="font-dmmono">
              {JSON.stringify(JSON.parse(artifact.content), null, 2)}
            </code>
          </pre>
        ) : artifact.type === 'html' ? (
          <div className="rounded-lg border border-border/30 bg-white p-4">
            <div dangerouslySetInnerHTML={{ __html: artifact.content }} />
          </div>
        ) : (
          <div className="prose prose-invert max-w-none font-geist">
            <MarkdownRenderer>{artifact.content}</MarkdownRenderer>
          </div>
        )}
      </div>
    </div>
  )
}

export default ArtifactViewer
