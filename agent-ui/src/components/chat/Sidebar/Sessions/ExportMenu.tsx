'use client'

import { useState } from 'react'
import { Button } from '../../../ui/button'
import Icon from '@/components/ui/icon'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger
} from '../../../ui/dropdown-menu'
import { toast } from 'sonner'
import {
  exportChatToMarkdown,
  exportPromptsForLLM,
  generateShareableLink,
  copyToClipboard,
  downloadAsFile
} from '@/lib/exportUtils'
import { useStore } from '@/store'
import { useQueryState } from 'nuqs'

interface ExportMenuProps {
  sessionId: string
  sessionName: string
}

const ExportMenu = ({ sessionId, sessionName }: ExportMenuProps) => {
  const { messages, selectedEndpoint, mode } = useStore()
  const [agentId] = useQueryState('agent')
  const [teamId] = useQueryState('team')
  const [isOpen, setIsOpen] = useState(false)

  const entityId = mode === 'agent' ? agentId : teamId

  const handleExportMarkdown = () => {
    if (messages.length === 0) {
      toast.error('No messages to export')
      return
    }

    const markdown = exportChatToMarkdown(messages, sessionName)
    const filename = `${sessionName.replace(/[^a-z0-9]/gi, '_')}_${new Date().getTime()}.md`
    downloadAsFile(markdown, filename)
    toast.success('Chat exported as Markdown')
    setIsOpen(false)
  }

  const handleExportPrompts = (provider: 'claude' | 'openai' | 'gemini' | 'mistral') => {
    if (messages.length === 0) {
      toast.error('No messages to export')
      return
    }

    const prompts = exportPromptsForLLM(messages, provider)
    const filename = `prompts_${provider}_${new Date().getTime()}.md`
    downloadAsFile(prompts, filename)
    toast.success(`Prompts exported for ${provider.toUpperCase()}`)
    setIsOpen(false)
  }

  const handleCopyShareLink = async () => {
    if (!entityId) {
      toast.error('No agent or team selected')
      return
    }

    const shareLink = generateShareableLink(
      sessionId,
      entityId,
      mode,
      selectedEndpoint
    )
    const success = await copyToClipboard(shareLink)

    if (success) {
      toast.success('Share link copied to clipboard')
    } else {
      toast.error('Failed to copy link')
    }
    setIsOpen(false)
  }

  const handleCopyMessages = async () => {
    if (messages.length === 0) {
      toast.error('No messages to copy')
      return
    }

    const markdown = exportChatToMarkdown(messages, sessionName)
    const success = await copyToClipboard(markdown)

    if (success) {
      toast.success('Messages copied to clipboard')
    } else {
      toast.error('Failed to copy messages')
    }
    setIsOpen(false)
  }

  return (
    <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          className="h-8 w-8 transform opacity-0 transition-all duration-200 ease-in-out hover:bg-accent/50 group-hover:opacity-100"
          onClick={(e) => e.stopPropagation()}
        >
          <Icon type="share" size="xs" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-56 font-dmmono">
        <DropdownMenuItem 
          onClick={handleCopyShareLink}
          className="cursor-pointer rounded-xl py-2.5 transition-colors hover:bg-accent/80"
        >
          <Icon type="link" size="xs" className="mr-3" />
          <span className="text-xs font-medium uppercase">Copy share link</span>
        </DropdownMenuItem>
        <DropdownMenuItem 
          onClick={handleCopyMessages}
          className="cursor-pointer rounded-xl py-2.5 transition-colors hover:bg-accent/80"
        >
          <Icon type="clipboard" size="xs" className="mr-3" />
          <span className="text-xs font-medium uppercase">Copy to clipboard</span>
        </DropdownMenuItem>
        <DropdownMenuSeparator className="my-1" />
        <DropdownMenuItem 
          onClick={handleExportMarkdown}
          className="cursor-pointer rounded-xl py-2.5 transition-colors hover:bg-accent/80"
        >
          <Icon type="download" size="xs" className="mr-3" />
          <span className="text-xs font-medium uppercase">Export as Markdown</span>
        </DropdownMenuItem>
        <DropdownMenuSub>
          <DropdownMenuSubTrigger className="cursor-pointer rounded-xl py-2.5 transition-colors hover:bg-accent/80">
            <Icon type="sparkles" size="xs" className="mr-3" />
            <span className="text-xs font-medium uppercase">Export for LLM</span>
          </DropdownMenuSubTrigger>
          <DropdownMenuSubContent className="font-dmmono">
            <DropdownMenuItem 
              onClick={() => handleExportPrompts('claude')}
              className="cursor-pointer rounded-xl py-2.5 transition-colors hover:bg-accent/80"
            >
              <Icon type="anthropic" size="xs" className="mr-3" />
              <span className="text-xs font-medium uppercase">Claude</span>
            </DropdownMenuItem>
            <DropdownMenuItem 
              onClick={() => handleExportPrompts('openai')}
              className="cursor-pointer rounded-xl py-2.5 transition-colors hover:bg-accent/80"
            >
              <Icon type="open-ai" size="xs" className="mr-3" />
              <span className="text-xs font-medium uppercase">ChatGPT</span>
            </DropdownMenuItem>
            <DropdownMenuItem 
              onClick={() => handleExportPrompts('gemini')}
              className="cursor-pointer rounded-xl py-2.5 transition-colors hover:bg-accent/80"
            >
              <Icon type="gemini" size="xs" className="mr-3" />
              <span className="text-xs font-medium uppercase">Gemini</span>
            </DropdownMenuItem>
            <DropdownMenuItem 
              onClick={() => handleExportPrompts('mistral')}
              className="cursor-pointer rounded-xl py-2.5 transition-colors hover:bg-accent/80"
            >
              <Icon type="mistral" size="xs" className="mr-3" />
              <span className="text-xs font-medium uppercase">Mistral AI</span>
            </DropdownMenuItem>
          </DropdownMenuSubContent>
        </DropdownMenuSub>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

export default ExportMenu
