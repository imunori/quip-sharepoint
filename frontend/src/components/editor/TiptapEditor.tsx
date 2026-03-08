import { useEffect, useCallback, useRef, useMemo, useState } from 'react';
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Collaboration from '@tiptap/extension-collaboration';
import CollaborationCursor from '@tiptap/extension-collaboration-cursor';
import * as Y from 'yjs';
import { WebsocketProvider } from 'y-websocket';
import {
  Bold, Italic, Strikethrough, Code, List, ListOrdered,
  Heading1, Heading2, Heading3, Quote, Undo, Redo, Save,
  Users, Wifi, WifiOff,
} from 'lucide-react';
import { useDocumentStore } from '../../store/documentStore';

const COLORS = ['#f44336','#e91e63','#9c27b0','#2196f3','#009688','#ff9800','#795548','#607d8b'];
const randomColor = () => COLORS[Math.floor(Math.random() * COLORS.length)];

const WS_PROTO = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const WS_BASE = `${WS_PROTO}//${window.location.host}`;

export function TiptapEditor() {
  const { currentDocument, saveDocument, currentUser } = useDocumentStore();
  const saveTimerRef = useRef<ReturnType<typeof setTimeout>>(undefined);
  const [connected, setConnected] = useState(false);
  const [peerCount, setPeerCount] = useState(0);

  const docId = currentDocument?.thread.id;

  // Yjs document + provider per document
  const { ydoc, provider } = useMemo(() => {
    if (!docId) return { ydoc: null, provider: null };
    const ydoc = new Y.Doc();
    const provider = new WebsocketProvider(WS_BASE + '/ws/yjs', docId, ydoc, {
      connect: true,
    });

    // Set local user awareness
    provider.awareness.setLocalStateField('user', {
      name: currentUser?.name || 'Anonymous',
      color: randomColor(),
    });

    return { ydoc, provider };
  }, [docId]);

  // Track connection and peers
  useEffect(() => {
    if (!provider) return;
    const onStatus = ({ status }: { status: string }) => setConnected(status === 'connected');
    const onAwareness = () => {
      const states = provider.awareness.getStates();
      setPeerCount(states.size);
    };
    provider.on('status', onStatus);
    provider.awareness.on('change', onAwareness);
    return () => {
      provider.off('status', onStatus);
      provider.awareness.off('change', onAwareness);
      provider.destroy();
      ydoc?.destroy();
    };
  }, [provider]);

  const editor = useEditor({
    extensions: [
      StarterKit.configure({ undoRedo: false }), // Yjs handles undo/redo
      ...(ydoc ? [
        Collaboration.configure({ document: ydoc }),
        CollaborationCursor.configure({
          provider: provider,
          user: {
            name: currentUser?.name || 'Anonymous',
            color: randomColor(),
          },
        }),
      ] : []),
    ],
    content: '',
    onUpdate: ({ editor }) => {
      if (saveTimerRef.current) clearTimeout(saveTimerRef.current);
      saveTimerRef.current = setTimeout(() => {
        if (currentDocument) {
          saveDocument(currentDocument.thread.id, editor.getHTML());
        }
      }, 2000);
    },
  }, [docId]);

  // Load initial content from server if Yjs doc is empty
  useEffect(() => {
    if (editor && currentDocument && ydoc) {
      const fragment = ydoc.getXmlFragment('default');
      // Only set content if the Yjs doc is empty (no prior collaboration state)
      if (fragment.length === 0 && currentDocument.html) {
        editor.commands.setContent(currentDocument.html);
      }
    }
  }, [editor, docId]);

  const handleSave = useCallback(() => {
    if (editor && currentDocument) {
      saveDocument(currentDocument.thread.id, editor.getHTML());
    }
  }, [editor, currentDocument]);

  if (!editor) return null;

  return (
    <div className="editor-container">
      <div className="editor-toolbar">
        <button className="toolbar-btn" onClick={() => editor.chain().focus().toggleBold().run()}
          data-active={editor.isActive('bold')} title="Bold">
          <Bold size={16} />
        </button>
        <button className="toolbar-btn" onClick={() => editor.chain().focus().toggleItalic().run()}
          data-active={editor.isActive('italic')} title="Italic">
          <Italic size={16} />
        </button>
        <button className="toolbar-btn" onClick={() => editor.chain().focus().toggleStrike().run()}
          data-active={editor.isActive('strike')} title="Strikethrough">
          <Strikethrough size={16} />
        </button>
        <button className="toolbar-btn" onClick={() => editor.chain().focus().toggleCode().run()}
          data-active={editor.isActive('code')} title="Code">
          <Code size={16} />
        </button>
        <span className="toolbar-divider" />
        <button className="toolbar-btn" onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
          data-active={editor.isActive('heading', { level: 1 })} title="Heading 1">
          <Heading1 size={16} />
        </button>
        <button className="toolbar-btn" onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
          data-active={editor.isActive('heading', { level: 2 })} title="Heading 2">
          <Heading2 size={16} />
        </button>
        <button className="toolbar-btn" onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()}
          data-active={editor.isActive('heading', { level: 3 })} title="Heading 3">
          <Heading3 size={16} />
        </button>
        <span className="toolbar-divider" />
        <button className="toolbar-btn" onClick={() => editor.chain().focus().toggleBulletList().run()}
          data-active={editor.isActive('bulletList')} title="Bullet List">
          <List size={16} />
        </button>
        <button className="toolbar-btn" onClick={() => editor.chain().focus().toggleOrderedList().run()}
          data-active={editor.isActive('orderedList')} title="Ordered List">
          <ListOrdered size={16} />
        </button>
        <button className="toolbar-btn" onClick={() => editor.chain().focus().toggleBlockquote().run()}
          data-active={editor.isActive('blockquote')} title="Blockquote">
          <Quote size={16} />
        </button>
        <span className="toolbar-divider" />
        <button className="toolbar-btn" onClick={() => editor.commands.undo()} title="Undo">
          <Undo size={16} />
        </button>
        <button className="toolbar-btn" onClick={() => editor.commands.redo()} title="Redo">
          <Redo size={16} />
        </button>
        <span className="toolbar-spacer" />
        <div className="toolbar-status">
          {connected ? <Wifi size={14} className="status-connected" /> : <WifiOff size={14} className="status-disconnected" />}
          {peerCount > 1 && (
            <span className="peer-count" title={`${peerCount} users online`}>
              <Users size={14} /> {peerCount}
            </span>
          )}
        </div>
        <button className="toolbar-btn save-btn" onClick={handleSave} title="Save">
          <Save size={16} />
          <span>保存</span>
        </button>
      </div>
      <EditorContent editor={editor} className="editor-content" />
    </div>
  );
}
