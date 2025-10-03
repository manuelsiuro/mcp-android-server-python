import type { ContentBlock } from '../types/claude';
import { TextContent } from './TextContent';
import { ToolUseBlock } from './ToolUseBlock';

interface ContentBlockRendererProps {
  block: ContentBlock;
  isStreaming?: boolean;
}

export function ContentBlockRenderer({ block, isStreaming }: ContentBlockRendererProps) {
  switch (block.type) {
    case 'text':
      return <TextContent text={block.text} isStreaming={isStreaming} />;

    case 'tool_use':
      return <ToolUseBlock toolUse={block} />;

    default:
      return null;
  }
}
