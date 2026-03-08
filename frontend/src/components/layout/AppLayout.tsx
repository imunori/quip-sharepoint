import { Header } from './Header';
import { FolderTree } from '../sidebar/FolderTree';
import { TiptapEditor } from '../editor/TiptapEditor';
import { SpreadsheetEditor } from '../editor/SpreadsheetEditor';
import { ThreadMessages } from '../chat/ThreadMessages';
import { DocumentLibrary } from '../documents/DocumentLibrary';
import { useDocumentStore } from '../../store/documentStore';
import { ArrowLeft, Trash2 } from 'lucide-react';

export function AppLayout() {
  const { currentDocument, sidebarOpen, view, clearCurrentDocument, deleteDocument } = useDocumentStore();

  const isSpreadsheet = currentDocument?.thread.type === 'spreadsheet';

  return (
    <div className="app-layout">
      <Header />
      <div className="app-body">
        {sidebarOpen && (
          <aside className="sidebar">
            <FolderTree />
          </aside>
        )}
        <main className="main-content">
          {view === 'editor' && currentDocument ? (
            <div className="document-view">
              <div className="document-title-bar">
                <button className="icon-btn" onClick={clearCurrentDocument} title="戻る">
                  <ArrowLeft size={18} />
                </button>
                <h2>{currentDocument.thread.title}</h2>
                {isSpreadsheet && <span className="doc-type-badge">スプレッドシート</span>}
                <span className="title-spacer" />
                <button
                  className="icon-btn danger-btn"
                  onClick={() => {
                    if (confirm(`「${currentDocument.thread.title}」を削除しますか？`)) {
                      deleteDocument(currentDocument.thread.id);
                    }
                  }}
                  title="削除"
                >
                  <Trash2 size={16} />
                </button>
              </div>
              {isSpreadsheet ? (
                <SpreadsheetEditor threadId={currentDocument.thread.id} />
              ) : (
                <TiptapEditor />
              )}
              <ThreadMessages />
            </div>
          ) : (
            <DocumentLibrary />
          )}
        </main>
      </div>
    </div>
  );
}
