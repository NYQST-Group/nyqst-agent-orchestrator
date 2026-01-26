import { useState, useRef, useEffect, useCallback, Suspense } from 'react';
import { Send, Paperclip, Bot, User, Loader2, StopCircle, RefreshCw } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { ChatThreadSkeleton, ChatMessageSkeleton } from '@/components/async/loading-states';
import { AsyncBoundary } from '@/components/async/suspense-wrapper';
import { useWorkspaceStore } from '@/stores/workspace-store';
import type { ThreadMessage, UUID } from '@/types';

interface ChatPaneProps {
  paneId: string;
}

// Mock data for demonstration
const MOCK_MESSAGES: ThreadMessage[] = [
  {
    id: '1',
    role: 'user',
    content: 'Analyze the compliance documents in the uploaded bundle and identify key regulatory requirements.',
    attachments: [],
    createdAt: new Date(Date.now() - 300000).toISOString(),
    metadata: {},
  },
  {
    id: '2',
    role: 'assistant',
    content: `I'll analyze the compliance documents in the uploaded bundle. Let me start by examining the structure and identifying key regulatory requirements.

**Initial Findings:**

1. **Data Protection Requirements** (GDPR Article 5)
   - Personal data must be processed lawfully, fairly, and transparently
   - Data minimization principles apply

2. **Financial Reporting** (SOX Compliance)
   - Internal controls over financial reporting required
   - CEO/CFO certification mandated

3. **Security Controls** (ISO 27001)
   - Information security management system required
   - Risk assessment procedures documented

I've created 12 claims linked to evidence spans across 5 documents. Would you like me to elaborate on any specific requirement?`,
    attachments: ['artifact-123', 'artifact-124'],
    toolCalls: [
      { id: 'tc-1', toolName: 'kb_query', args: { query: 'regulatory requirements', topK: 10 } },
      { id: 'tc-2', toolName: 'create_claim', args: { type: 'requirement', count: 12 } },
    ],
    createdAt: new Date(Date.now() - 240000).toISOString(),
    metadata: { tokensUsed: 1250 },
  },
  {
    id: '3',
    role: 'user',
    content: 'Show me the evidence spans for the GDPR requirements.',
    attachments: [],
    createdAt: new Date(Date.now() - 180000).toISOString(),
    metadata: {},
  },
];

export function ChatPane({ paneId }: ChatPaneProps) {
  const [messages, setMessages] = useState<ThreadMessage[]>(MOCK_MESSAGES);
  const [input, setInput] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const { pinnedItems } = useWorkspaceStore();

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    if (scrollAreaRef.current) {
      const scrollContainer = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]');
      if (scrollContainer) {
        scrollContainer.scrollTop = scrollContainer.scrollHeight;
      }
    }
  }, [messages]);

  const handleSend = useCallback(async () => {
    if (!input.trim() || isStreaming) return;

    const userMessage: ThreadMessage = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content: input.trim(),
      attachments: [],
      createdAt: new Date().toISOString(),
      metadata: {},
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsStreaming(true);

    // Simulate streaming response
    setTimeout(() => {
      const assistantMessage: ThreadMessage = {
        id: `msg-${Date.now() + 1}`,
        role: 'assistant',
        content: 'I understand your request. Let me process that for you...\n\n(This is a mock response demonstrating the streaming UI pattern.)',
        attachments: [],
        createdAt: new Date().toISOString(),
        metadata: { tokensUsed: 150 },
      };
      setMessages((prev) => [...prev, assistantMessage]);
      setIsStreaming(false);
    }, 1500);
  }, [input, isStreaming]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSend();
      }
    },
    [handleSend]
  );

  const handleStop = useCallback(() => {
    setIsStreaming(false);
  }, []);

  return (
    <div className="h-full flex flex-col">
      {/* Pinned context indicator */}
      {pinnedItems.length > 0 && (
        <div className="px-4 py-2 border-b bg-muted/30 flex items-center gap-2 flex-wrap">
          <span className="text-xs text-muted-foreground">Context:</span>
          {pinnedItems.slice(0, 3).map((item) => (
            <Badge key={item.id} variant="outline" className="text-xs">
              {item.type}: {item.label || item.id.slice(0, 8)}
            </Badge>
          ))}
          {pinnedItems.length > 3 && (
            <Badge variant="outline" className="text-xs">
              +{pinnedItems.length - 3} more
            </Badge>
          )}
        </div>
      )}

      {/* Messages */}
      <ScrollArea ref={scrollAreaRef} className="flex-1 px-4">
        <AsyncBoundary loadingFallback={<ChatThreadSkeleton />}>
          <div className="py-4 space-y-4">
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
            {isStreaming && (
              <div className="flex gap-3">
                <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
                  <Bot className="h-4 w-4 text-primary" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-sm font-medium">Assistant</span>
                    <Loader2 className="h-3 w-3 animate-spin text-muted-foreground" />
                  </div>
                  <div className="bg-muted rounded-lg p-3">
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <span className="animate-pulse">Thinking...</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </AsyncBoundary>
      </ScrollArea>

      {/* Input area */}
      <div className="border-t p-4">
        <div className="flex items-center gap-2">
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon" disabled={isStreaming}>
                <Paperclip className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>Attach file</TooltipContent>
          </Tooltip>

          <Input
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type a message..."
            disabled={isStreaming}
            className="flex-1"
          />

          {isStreaming ? (
            <Button variant="destructive" size="icon" onClick={handleStop}>
              <StopCircle className="h-4 w-4" />
            </Button>
          ) : (
            <Button
              variant="default"
              size="icon"
              onClick={handleSend}
              disabled={!input.trim()}
            >
              <Send className="h-4 w-4" />
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}

function ChatMessage({ message }: { message: ThreadMessage }) {
  const isUser = message.role === 'user';

  return (
    <div className={cn('flex gap-3', isUser ? 'flex-row-reverse' : 'flex-row')}>
      <div
        className={cn(
          'h-8 w-8 rounded-full flex items-center justify-center shrink-0',
          isUser ? 'bg-primary text-primary-foreground' : 'bg-primary/10'
        )}
      >
        {isUser ? (
          <User className="h-4 w-4" />
        ) : (
          <Bot className="h-4 w-4 text-primary" />
        )}
      </div>

      <div className={cn('flex-1 max-w-[80%]', isUser && 'flex flex-col items-end')}>
        <div className="flex items-center gap-2 mb-1">
          <span className="text-sm font-medium">
            {isUser ? 'You' : 'Assistant'}
          </span>
          <span className="text-xs text-muted-foreground">
            {new Date(message.createdAt).toLocaleTimeString()}
          </span>
        </div>

        <div
          className={cn(
            'rounded-lg p-3',
            isUser ? 'bg-primary text-primary-foreground' : 'bg-muted'
          )}
        >
          <p className="text-sm whitespace-pre-wrap">{message.content}</p>

          {/* Tool calls */}
          {message.toolCalls && message.toolCalls.length > 0 && (
            <div className="mt-2 pt-2 border-t border-border/50 space-y-1">
              {message.toolCalls.map((tc) => (
                <div key={tc.id} className="flex items-center gap-2 text-xs opacity-70">
                  <Badge variant="outline" className="text-xs">
                    {tc.toolName}
                  </Badge>
                </div>
              ))}
            </div>
          )}

          {/* Attachments */}
          {message.attachments.length > 0 && (
            <div className="mt-2 pt-2 border-t border-border/50 flex flex-wrap gap-1">
              {message.attachments.map((att) => (
                <Badge key={att} variant="artifact" className="text-xs">
                  {att.slice(0, 12)}...
                </Badge>
              ))}
            </div>
          )}
        </div>

        {/* Token usage */}
        {message.metadata.tokensUsed && (
          <span className="text-xs text-muted-foreground mt-1">
            {message.metadata.tokensUsed} tokens
          </span>
        )}
      </div>
    </div>
  );
}
