'use client'

import ChatInput from './ChatInput'
import MessageArea from './MessageArea'
import ArtifactViewer from './Artifacts/ArtifactViewer'
import { useStore } from '@/store'
import { motion, AnimatePresence } from 'framer-motion'

const ChatArea = () => {
  const { currentArtifact, artifactPanelOpen, setArtifactPanelOpen, setCurrentArtifact } = useStore()

  const handleCloseArtifact = () => {
    setArtifactPanelOpen(false)
    // Delay clearing the artifact to allow for exit animation
    setTimeout(() => setCurrentArtifact(null), 300)
  }

  return (
    <main className="relative m-1.5 flex flex-grow gap-1.5 overflow-hidden rounded-xl">
      {/* Chat Area */}
      <div className={`flex flex-grow flex-col bg-background rounded-xl transition-all duration-300 ${
        artifactPanelOpen ? 'max-w-[50%]' : 'max-w-full'
      }`}>
        <MessageArea />
        <div className="sticky bottom-0 ml-9 px-4 pb-2">
          <ChatInput />
        </div>
      </div>

      {/* Artifact Panel */}
      <AnimatePresence>
        {artifactPanelOpen && currentArtifact && (
          <motion.div
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: '50%', opacity: 1 }}
            exit={{ width: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: 'easeInOut' }}
            className="flex-shrink-0 overflow-hidden rounded-xl border border-border/30 bg-background"
          >
            <ArtifactViewer
              artifact={currentArtifact}
              onClose={handleCloseArtifact}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </main>
  )
}

export default ChatArea
