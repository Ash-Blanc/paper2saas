import { memo, useEffect } from 'react'
import Icon from '@/components/ui/icon'
import MarkdownRenderer from '@/components/ui/typography/MarkdownRenderer'
import { useStore } from '@/store'
import type { ChatMessage } from '@/types/os'
import Videos from './Multimedia/Videos'
import Images from './Multimedia/Images'
import Audios from './Multimedia/Audios'
import AgentThinkingLoader from './AgentThinkingLoader'
import { detectArtifact } from '@/lib/artifactDetection'
import { Button } from '@/components/ui/button'

interface MessageProps {
  message: ChatMessage
}

const AgentMessage = ({ message }: MessageProps) => {
  const { streamingErrorMessage, setCurrentArtifact, setArtifactPanelOpen } = useStore()
  
  // Detect artifacts in message content
  const artifactResult = message.content 
    ? detectArtifact(message.content, `${message.created_at}`)
    : { hasArtifact: false, cleanedContent: message.content || '' }

  // Auto-open artifact panel for detected artifacts
  useEffect(() => {
    if (artifactResult.hasArtifact && artifactResult.artifact) {
      setCurrentArtifact(artifactResult.artifact)
      setArtifactPanelOpen(true)
    }
  }, [artifactResult.hasArtifact, artifactResult.artifact, setCurrentArtifact, setArtifactPanelOpen])

  const handleViewArtifact = () => {
    if (artifactResult.artifact) {
      setCurrentArtifact(artifactResult.artifact)
      setArtifactPanelOpen(true)
    }
  }

  let messageContent
  if (message.streamingError) {
    messageContent = (
      <p className="text-destructive">
        Oops! Something went wrong while streaming.{' '}
        {streamingErrorMessage ? (
          <>{streamingErrorMessage}</>
        ) : (
          'Please try refreshing the page or try again later.'
        )}
      </p>
    )
  } else if (message.content) {
    const contentToDisplay = artifactResult.cleanedContent || message.content
    
    messageContent = (
      <div className="flex w-full flex-col gap-4">
        {artifactResult.hasArtifact && artifactResult.artifact && (
          <div className="flex items-center gap-2 rounded-lg border border-primary/20 bg-primary/5 p-3">
            <Icon type="sparkles" size="xs" className="text-primary" />
            <div className="flex-1">
              <p className="text-xs font-medium text-primary">
                {artifactResult.artifact.title}
              </p>
              <p className="text-xs text-muted">
                {artifactResult.artifact.type} artifact
              </p>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleViewArtifact}
              className="text-xs"
            >
              View
            </Button>
          </div>
        )}
        {contentToDisplay && (
          <MarkdownRenderer>{contentToDisplay}</MarkdownRenderer>
        )}
        {message.videos && message.videos.length > 0 && (
          <Videos videos={message.videos} />
        )}
        {message.images && message.images.length > 0 && (
          <Images images={message.images} />
        )}
        {message.audio && message.audio.length > 0 && (
          <Audios audio={message.audio} />
        )}
      </div>
    )
  } else if (message.response_audio) {
    if (!message.response_audio.transcript) {
      messageContent = (
        <div className="mt-2 flex items-start">
          <AgentThinkingLoader />
        </div>
      )
    } else {
      messageContent = (
        <div className="flex w-full flex-col gap-4">
          <MarkdownRenderer>
            {message.response_audio.transcript}
          </MarkdownRenderer>
          {message.response_audio.content && message.response_audio && (
            <Audios audio={[message.response_audio]} />
          )}
        </div>
      )
    }
  } else {
    messageContent = (
      <div className="mt-2">
        <AgentThinkingLoader />
      </div>
    )
  }

  return (
    <div className="flex flex-row items-start gap-4 font-geist">
      <div className="flex-shrink-0">
        <Icon type="agent" size="sm" />
      </div>
      {messageContent}
    </div>
  )
}

const UserMessage = memo(({ message }: MessageProps) => {
  return (
    <div className="flex items-start gap-4 pt-4 text-start max-md:break-words">
      <div className="flex-shrink-0">
        <Icon type="user" size="sm" />
      </div>
      <div className="text-md rounded-lg font-geist text-secondary">
        {message.content}
      </div>
    </div>
  )
})

AgentMessage.displayName = 'AgentMessage'
UserMessage.displayName = 'UserMessage'
export { AgentMessage, UserMessage }
