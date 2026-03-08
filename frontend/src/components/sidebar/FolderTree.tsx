import { useEffect, useState } from 'react';
import { Folder, FileText, ChevronRight, ChevronDown, FolderPlus } from 'lucide-react';
import { useDocumentStore } from '../../store/documentStore';
import type { QuipFolder } from '../../types';

function FolderItem({ folder, onSelect }: { folder: QuipFolder; onSelect: (id: string) => void }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="folder-item">
      <div className="folder-row" onClick={() => { setExpanded(!expanded); onSelect(folder.folder.id); }}>
        {expanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
        <Folder size={16} className={`folder-icon folder-color-${folder.folder.color}`} />
        <span className="folder-name">{folder.folder.title}</span>
      </div>
    </div>
  );
}

export function FolderTree() {
  const { folders, documents, loadFolders, loadRecentDocuments, selectDocument, selectFolder, createFolder } = useDocumentStore();

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
        <span className="folder-tree-title">ドキュメント</span>
        <button className="icon-btn icon-btn-sm" onClick={handleNewFolder} title="新規フォルダ">
          <FolderPlus size={16} />
        </button>
      </div>

      <div className="folder-list">
        {folders.map((f) => (
          <FolderItem key={f.folder.id} folder={f} onSelect={selectFolder} />
        ))}
      </div>

      <div className="recent-docs">
        <div className="section-title">最近のドキュメント</div>
        {documents.map((doc) => (
          <div
            key={doc.thread.id}
            className="doc-item"
            onClick={() => selectDocument(doc.thread.id)}
          >
            <FileText size={14} />
            <span className="doc-name">{doc.thread.title}</span>
          </div>
        ))}
        {documents.length === 0 && (
          <div className="empty-state">ドキュメントがありません</div>
        )}
      </div>
    </div>
  );
}
