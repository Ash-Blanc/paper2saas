export type ArtifactType = 
  | 'markdown'
  | 'code'
  | 'html'
  | 'report'
  | 'json'
  | 'table'
  | 'mermaid'
  | 'chart';

export interface Artifact {
  id: string;
  type: ArtifactType;
  title: string;
  content: string;
  language?: string; // For code artifacts
  metadata?: {
    createdAt: number;
    messageId: string;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    [key: string]: any;
  };
}

export interface ArtifactDetectionResult {
  hasArtifact: boolean;
  artifact?: Artifact;
  cleanedContent: string; // Content with artifact markers removed
}
