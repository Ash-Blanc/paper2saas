import { Artifact, ArtifactDetectionResult, ArtifactType } from '@/types/artifacts';

/**
 * Detects artifacts in message content using XML-style tags or markdown code blocks
 * Supports formats like:
 * <artifact type="report" title="Analysis Report">content</artifact>
 * or
 * ```report:Analysis Report
 * content
 * ```
 */
export function detectArtifact(content: string, messageId: string): ArtifactDetectionResult {
  // Try XML-style artifact tags first
  const xmlMatch = content.match(/<artifact\s+type="([^"]+)"\s+title="([^"]+)">([\s\S]*?)<\/artifact>/i);
  
  if (xmlMatch) {
    const [fullMatch, type, title, artifactContent] = xmlMatch;
    return {
      hasArtifact: true,
      artifact: {
        id: `artifact-${messageId}-${Date.now()}`,
        type: type as ArtifactType,
        title: title,
        content: artifactContent.trim(),
        metadata: {
          createdAt: Date.now(),
          messageId
        }
      },
      cleanedContent: content.replace(fullMatch, '').trim()
    };
  }

  // Try code block with artifact syntax: ```artifactType:Title
  const codeBlockMatch = content.match(/```(report|markdown|json|html|mermaid|chart):([^\n]+)\n([\s\S]*?)```/);
  
  if (codeBlockMatch) {
    const [fullMatch, type, title, artifactContent] = codeBlockMatch;
    return {
      hasArtifact: true,
      artifact: {
        id: `artifact-${messageId}-${Date.now()}`,
        type: type as ArtifactType,
        title: title.trim(),
        content: artifactContent.trim(),
        metadata: {
          createdAt: Date.now(),
          messageId
        }
      },
      cleanedContent: content.replace(fullMatch, '').trim()
    };
  }

  // Check for report-like content (heuristic detection)
  if (content.includes('# Paper-to-SaaS Opportunity Report') || 
      content.includes('## Executive Summary') ||
      (content.includes('##') && content.length > 1000)) {
    return {
      hasArtifact: true,
      artifact: {
        id: `artifact-${messageId}-${Date.now()}`,
        type: 'report',
        title: extractReportTitle(content),
        content: content,
        metadata: {
          createdAt: Date.now(),
          messageId,
          autoDetected: true
        }
      },
      cleanedContent: '' // For auto-detected reports, show in artifact only
    };
  }

  // Check for large code blocks (potential artifacts)
  const largeCodeMatch = content.match(/```(\w+)\n([\s\S]{500,})```/);
  if (largeCodeMatch) {
    const [fullMatch, language, codeContent] = largeCodeMatch;
    return {
      hasArtifact: true,
      artifact: {
        id: `artifact-${messageId}-${Date.now()}`,
        type: 'code',
        title: `Code (${language})`,
        content: codeContent.trim(),
        language: language,
        metadata: {
          createdAt: Date.now(),
          messageId,
          autoDetected: true
        }
      },
      cleanedContent: content.replace(fullMatch, `\n_[View full code in artifact panel]_\n`).trim()
    };
  }

  return {
    hasArtifact: false,
    cleanedContent: content
  };
}

/**
 * Extract a meaningful title from report content
 */
function extractReportTitle(content: string): string {
  // Try to extract from first heading
  const h1Match = content.match(/^#\s+(.+)$/m);
  if (h1Match) return h1Match[1];

  const h2Match = content.match(/^##\s+(.+)$/m);
  if (h2Match) return h2Match[1];

  // Check for "Paper2SaaS" patterns
  if (content.includes('Paper2SaaS') || content.includes('Paper-to-SaaS')) {
    return 'Paper2SaaS Analysis Report';
  }

  return 'Analysis Report';
}

/**
 * Format artifact content based on type
 */
export function formatArtifactContent(artifact: Artifact): string {
  switch (artifact.type) {
    case 'json':
      try {
        const parsed = JSON.parse(artifact.content);
        return JSON.stringify(parsed, null, 2);
      } catch {
        return artifact.content;
      }
    case 'code':
    case 'markdown':
    case 'report':
    case 'html':
    case 'mermaid':
    case 'chart':
    case 'table':
    default:
      return artifact.content;
  }
}
