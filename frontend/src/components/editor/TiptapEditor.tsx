import { useEffect, useCallback, useRef } from 'react';
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import {
  Bold, Italic, Strikethrough, Code, List, ListOrdered,
  Heading1, Heading2, Heading3, Quote, Undo, Redo, Save,
} from 'lucide-react';
import { useDocumentStore } from '../../store/documentStore';

export function TiptapEditor() {
  const { currentDocument, saveDocument } = useDocumentStore();
  const saveTimerRef = useRef<ReturnType<typeof setTimeout>>(undefined);

  const editor = useEditor({
    extensions: [StarterKit],
    content: currentDocument?.html || '<p></p>',
    onUpdate: ({ editor }) => {
      // Auto-save with debounce
      if (saveTimerRef.current) clearTimeout(saveTimerRef.current);
      saveTimerRef.current = setTimeout(() => {
        if (currentDocument) {
          saveDocument(currentDocument.thread.id, editor.getHTML());
        }
      }, 1000);
    },
  });

  // Update editor content when document changes
  useEffect(() => {
    if (editor && currentDocument) {
      const currentContent = editor.getHTML();
      if (currentContent !== currentDocument.html) {
        editor.commands.setContent(currentDocument.html || '<p></p>');
      }
    }
  }, [currentDocument?.thread.id]);

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
          data-active={editor.isActive('bold')}>
          <Bold size={16} />
        </button>
        <button className="toolbar-btn" onClick={() => editor.chain().focus().toggleItalic().run()}
          data-active={editor.isActive('italic')}>
          <Italic size={16} />
        </button>
        <button className="toolbar-btn" onClick={() => editor.chain().focus().toggleStrike().run()}
          data-active={editor.isActive('strike')}>
          <Strikethrough size={16} />
        </button>
        <button className="toolbar-btn" onClick={() => editor.chain().focus().toggleCode().run()}
          data-active={editor.isActive('code')}>
          <Code size={16} />
        </button>
        <span className="toolbar-divider" />
        <button className="toolbar-btn" onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
          data-active={editor.isActive('heading', { level: 1 })}>
          <Heading1 size={16} />
        </button>
        <button className="toolbar-btn" onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
          data-active={editor.isActive('heading', { level: 2 })}>
          <Heading2 size={16} />
        </button>
        <button className="toolbar-btn" onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()}
          data-active={editor.isActive('heading', { level: 3 })}>
          <Heading3 size={16} />
        </button>
        <span className="toolbar-divider" />
        <button className="toolbar-btn" onClick={() => editor.chain().focus().toggleBulletList().run()}
          data-active={editor.isActive('bulletList')}>
          <List size={16} />
        </button>
        <button className="toolbar-btn" onClick={() => editor.chain().focus().toggleOrderedList().run()}
          data-active={editor.isActive('orderedList')}>
          <ListOrdered size={16} />
        </button>
        <button className="toolbar-btn" onClick={() => editor.chain().focus().toggleBlockquote().run()}
          data-active={editor.isActive('blockquote')}>
          <Quote size={16} />
        </button>
        <span className="toolbar-divider" />
        <button className="toolbar-btn" onClick={() => editor.chain().focus().undo().run()}>
          <Undo size={16} />
        </button>
        <button className="toolbar-btn" onClick={() => editor.chain().focus().redo().run()}>
          <Redo size={16} />
        </button>
        <span className="toolbar-spacer" />
        <button className="toolbar-btn save-btn" onClick={handleSave}>
          <Save size={16} />
          <span>保存</span>
        </button>
      </div>
      <EditorContent editor={editor} className="editor-content" />
    </div>
  );
}
