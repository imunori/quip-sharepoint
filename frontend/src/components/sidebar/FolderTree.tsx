import { useEffect, useState } from 'react';
import {
  Folder, FolderOpen, FileText, ChevronRight, ChevronDown, FolderPlus,
} from 'lucide-react';
import { useDocumentStore } from '../../store/documentStore';
import type { QuipFolder } from '../../types';

function FolderItem({ folder, onSelectFolder }: {
  folder: QuipFolder;
  onSelectFolder: (id: string) => void;
}) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="folder-item">
      <div
        className="folder-row"
        onClick={() => { setExpanded(!expanded); onSelectFolder(folder.folder.id); }}
        draggable
        onDragOver={(e) => { e.preventDefault(); e.currentTarget.classList.add('drag-over'); }}
        onDragLeave={(e) => e.currentTarget.classList.remove('drag-over')}
        onDrop={(e) => {
          e.preventDefault();
          e.currentTarget.classList.remove('drag-over');
          const docId = e.dataTransfer.getData('text/document-id');
          if (docId) {
            // TODO: move document to folder
          }
        }}
      >
        {expanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
        {expanded ? <FolderOpen size={16} className="folder-icon" /> : <Folder size={16} className="folder-icon" />}
        <span className="folder-name">{folder.folder.title}</span>
        <span className="folder-count">{folder.children.length || ''}</span>
      </div>
    </div>
  );
}

export function FolderTree() {
  const {
    folders, documents, loadFolders, loadRecentDocuments,
    selectDocument, selectFolder, createFolder, currentDocument,
  } = useDocumentStore();

  useEffect(() => {
    loadFolders();
    loadRecentDocuments();
  }, []);

  const handleNewFolder = async () => {
    const title = prompt('フォルダ名を入力:');
    if (title) await createFolder(title);
  };

  return (
    <div className="folder-tree">
      <div className="folder-tree-header">
        <span className="folder-tree-title">フォルダ</span>
        <button className="icon-btn icon-btn-sm" onClick={handleNewFolder} title="新規フォルダ">
          <FolderPlus size={16} />
        </button>
      </div>

      <div className="folder-list">
        {folders.map((f) => (
          <FolderItem key={f.folder.id} folder={f} onSelectFolder={selectFolder} />
        ))}
        {folders.length === 0 && (
          <div className="empty-state-sm">フォルダなし</div>
        )}
      </div>

      <div className="recent-docs">
        <div className="section-title">最近のドキュメント</div>
        {documents.map((doc) => (
          <div
            key={doc.thread.id}
            className={`doc-item ${currentDocument?.thread.id === doc.thread.id ? 'active' : ''}`}
            onClick={() => selectDocument(doc.thread.id)}
            draggable
            onDragStart={(e) => {
              e.dataTransfer.setData('text/document-id', doc.thread.id);
              e.dataTransfer.effectAllowed = 'move';
            }}
          >
            <FileText size={14} />
            <span className="doc-name">{doc.thread.title}</span>
          </div>
        ))}
        {documents.length === 0 && (
          <div className="empty-state-sm">ドキュメントなし</div>
        )}
      </div>
    </div>
  );
}
