# Artifacts System - Claude-Style Implementation

## Overview
The agent-ui now supports Claude-style artifacts for rendering reports, code, and other structured content in a dedicated side panel.

## Features

### Automatic Detection
The system automatically detects artifacts in agent responses using:
1. **XML-style tags**: `<artifact type="report" title="Title">content</artifact>`
2. **Code block syntax**: ````report:Title\ncontent\n````
3. **Heuristic detection**: Auto-detects Paper2SaaS reports and large code blocks

### Supported Artifact Types
- `report` - Analysis reports (automatically detected for Paper2SaaS outputs)
- `markdown` - Markdown content
- `code` - Code snippets with syntax highlighting
- `json` - JSON data with formatting
- `html` - HTML content (rendered)
- `table` - Tabular data
- `mermaid` - Diagrams (future)
- `chart` - Charts and graphs (future)

## How It Works

### 1. Detection (`lib/artifactDetection.ts`)
When an agent message is received, the system:
- Scans content for artifact markers
- Extracts artifact metadata (type, title, content)
- Cleans the main message content
- Auto-detects Paper2SaaS reports by looking for report-like patterns

### 2. Storage (`store.ts`)
```typescript
currentArtifact: Artifact | null     // Currently displayed artifact
artifactPanelOpen: boolean           // Panel visibility state
setCurrentArtifact(artifact)         // Update displayed artifact
setArtifactPanelOpen(isOpen)         // Toggle panel
```

### 3. Display (`ChatArea/Artifacts/ArtifactViewer.tsx`)
- Side panel (50% width) with smooth animations
- Header with artifact type badge and title
- Action buttons: Copy, Download, Close
- Type-specific rendering:
  - Code: Syntax-highlighted code blocks
  - JSON: Formatted with indentation
  - HTML: Rendered in iframe-style container
  - Markdown/Report: Full markdown rendering

### 4. Message Integration (`Messages/MessageItem.tsx`)
- Automatically detects artifacts in agent messages
- Shows artifact indicator card with "View" button
- Auto-opens panel when artifact is detected
- Displays cleaned message content (without artifact)

## Usage Examples

### Backend (Agent Response)
Agents can explicitly create artifacts:

```python
# Option 1: XML-style (recommended)
response = """
Here's the analysis report:

<artifact type="report" title="Paper2SaaS Analysis Report">
# Analysis Results
## Executive Summary
...
</artifact>

The report shows...
"""

# Option 2: Code block syntax  
response = """
Here's the code:

```code:Implementation
def analyze_paper(arxiv_id):
    ...
```
"""

# Option 3: Automatic (for Paper2SaaS reports)
# Just return a report with standard headings - it will be auto-detected
response = """
# Paper-to-SaaS Opportunity Report

## Executive Summary
...
"""
```

### Frontend Behavior
1. **Auto-open**: Artifacts automatically open in side panel
2. **Manual view**: Click "View" button on artifact indicator
3. **Copy**: One-click copy to clipboard
4. **Download**: Download artifact as file (with proper extension)
5. **Close**: Close panel (can reopen from message)

## File Structure

```
agent-ui/src/
├── types/
│   └── artifacts.ts                 # Artifact type definitions
├── lib/
│   └── artifactDetection.ts        # Detection and extraction logic
├── components/chat/ChatArea/
│   ├── ChatArea.tsx                # Main layout with split view
│   ├── Artifacts/
│   │   ├── ArtifactViewer.tsx     # Artifact display component
│   │   └── index.ts               # Exports
│   └── Messages/
│       └── MessageItem.tsx        # Updated with artifact detection
└── store.ts                        # State management
```

## Customization

### Adding New Artifact Types
1. Add type to `types/artifacts.ts`:
   ```typescript
   export type ArtifactType = '...' | 'newtype';
   ```

2. Update detection in `artifactDetection.ts`:
   ```typescript
   // Add detection pattern
   ```

3. Update rendering in `ArtifactViewer.tsx`:
   ```typescript
   case 'newtype':
     return <CustomRenderer content={artifact.content} />
   ```

### Styling
- Panel width: Modify `ChatArea.tsx` (currently 50%)
- Colors: Uses design system tokens from `tailwind.config.ts`
- Animations: Framer Motion configs in `ChatArea.tsx`

## Benefits

1. **Clean UI**: Reports and code don't clutter the chat
2. **Better UX**: Dedicated space for viewing/copying artifacts
3. **Persistent**: Artifacts stay accessible in messages
4. **Flexible**: Multiple artifact types supported
5. **Automatic**: Paper2SaaS reports detected automatically

## Future Enhancements

- [ ] Mermaid diagram rendering
- [ ] Chart/graph rendering (Chart.js)
- [ ] Multi-artifact support (tabs/carousel)
- [ ] Artifact history/library
- [ ] Export to various formats (PDF, etc.)
- [ ] Collaborative features (share, comment)
- [ ] Version tracking for artifacts
