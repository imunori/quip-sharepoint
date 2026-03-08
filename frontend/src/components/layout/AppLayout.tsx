import { Header } from './Header';
import { FolderTree } from '../sidebar/FolderTree';
import { TiptapEditor } from '../editor/TiptapEditor';
import { ThreadMessages } from '../chat/ThreadMessages';
import { DocumentLibrary } from '../documents/DocumentLibrary';
import { useDocumentStore } from '../../store/documentStore';

export function AppLayout() {
  const { currentDocument, sidebarOpen } = useDocumentStore();

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
          {currentDocument ? (
            <div className="document-view">
              <div className="document-title-bar">
                <h2>{currentDocument.thread.title}</h2>
              </div>
              <TiptapEditor />
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
