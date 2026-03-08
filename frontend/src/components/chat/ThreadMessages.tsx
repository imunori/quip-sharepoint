import { useEffect, useState, useRef } from 'react';
import { Send, MessageSquare } from 'lucide-react';
import { quipApi } from '../../api/quipClient';
import { useDocumentStore } from '../../store/documentStore';
import type { QuipMessage } from '../../types';

export function ThreadMessages() {
  const { currentDocument } = useDocumentStore();
  const [messages, setMessages] = useState<QuipMessage[]>([]);
  const [input, setInput] = useState('');
  const [collapsed, setCollapsed] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  const threadId = currentDocument?.thread.id;

  useEffect(() => {
    if (!threadId) return;
    quipApi.getMessages(threadId).then(setMessages);
  }, [threadId]);

  const handleSend = async () => {
    if (!input.trim() || !threadId) return;
    const msg = await quipApi.postMessage(threadId, input.trim());
    setMessages((prev) => [...prev, msg]);
    setInput('');
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  if (!threadId) return null;

  return (
    <div className={`thread-messages ${collapsed ? 'collapsed' : ''}`}>
      <div className="messages-header" onClick={() => setCollapsed(!collapsed)}>
        <MessageSquare size={16} />
        <span>コメント ({messages.length})</span>
      </div>
      {!collapsed && (
        <>
          <div className="messages-list">
            {messages.map((msg) => (
              <div key={msg.id} className="message-item">
                <div className="message-meta">
                  <span className="message-author">{msg.author_id}</span>
                  <span className="message-time">
                    {new Date(msg.created_usec / 1000).toLocaleString('ja-JP')}
                  </span>
                </div>
                <div className="message-text">{msg.text}</div>
              </div>
            ))}
            <div ref={bottomRef} />
          </div>
          <div className="message-input-area">
            <input
              type="text"
              className="message-input"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="コメントを入力..."
            />
            <button className="icon-btn" onClick={handleSend}>
              <Send size={16} />
            </button>
          </div>
        </>
      )}
    </div>
  );
}
