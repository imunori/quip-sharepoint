import { useState, useRef, useCallback } from 'react';
import { FileText, Clock, Upload, Trash2, Edit3, MoreVertical, Grid, List as ListIcon } from 'lucide-react';
import { useDocumentStore } from '../../store/documentStore';
import type { QuipThread } from '../../types';

export function DocumentLibrary() {
  const {
    documents, searchResults, searchQuery, selectDocument,
    deleteDocument, renameDocument, createDocument, loading,
  } = useDocumentStore();
  const [viewMode, setViewMode] = useState<'table' | 'grid'>('table');
  const [dragOver, setDragOver] = useState(false);
  const [contextMenu, setContextMenu] = useState<{ x: number; y: number; doc: QuipThread } | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const displayDocs = searchQuery ? searchResults : documents;

  const handleFileDrop = useCallback(async (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const files = e.dataTransfer.files;
    for (const file of Array.from(files)) {
      if (file.type.startsWith('text/') || file.name.endsWith('.md') || file.name.endsWith('.txt')) {
        const title = file.name.replace(/\.[^/.]+$/, '');
        await createDocument(title);
      }
    }
  }, [createDocument]);

  const handleContextMenu = (e: React.MouseEvent, doc: QuipThread) => {
    e.preventDefault();
    setContextMenu({ x: e.clientX, y: e.clientY, doc });
  };

  const handleRename = async () => {
    if (!contextMenu) return;
    const newTitle = prompt('新しいタイトル:', contextMenu.doc.thread.title);
    if (newTitle && newTitle !== contextMenu.doc.thread.title) {
      await renameDocument(contextMenu.doc.thread.id, newTitle);
    }
    setContextMenu(null);
  };

  const handleDelete = async () => {
    if (!contextMenu) return;
    if (confirm(`「${contextMenu.doc.thread.title}」を削除しますか？`)) {
      await deleteDocument(contextMenu.doc.thread.id);
    }
    setContextMenu(null);
  };

  const formatDate = (usec: number) => {
    if (!usec) return '-';
    return new Date(usec / 1000).toLocaleString('ja-JP', {
      month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
    });
  };

  if (loading) {
    return <div className="loading">読み込み中...</div>;
  }

  return (
    <div
      className={`document-library ${dragOver ? 'drag-over-zone' : ''}`}
      onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
      onDragLeave={() => setDragOver(false)}
      onDrop={handleFileDrop}
      onClick={() => setContextMenu(null)}
    >
      <div className="library-header">
        <h2>{searchQuery ? `検索: "${searchQuery}"` : 'ドキュメントライブラリ'}</h2>
        <div className="library-actions">
          <button className="icon-btn" onClick={() => fileInputRef.current?.click()} title="ファイルアップロード">
            <Upload size={18} />
          </button>
          <input ref={fileInputRef} type="file" hidden multiple accept=".txt,.md,.html" />
          <button
            className={`icon-btn ${viewMode === 'table' ? 'active' : ''}`}
            onClick={() => setViewMode('table')} title="テーブル表示"
          >
            <ListIcon size={18} />
          </button>
          <button
            className={`icon-btn ${viewMode === 'grid' ? 'active' : ''}`}
            onClick={() => setViewMode('grid')} title="グリッド表示"
          >
            <Grid size={18} />
          </button>
        </div>
      </div>

      {dragOver && (
        <div className="drop-overlay">
          <Upload size={48} />
          <p>ファイルをドロップしてアップロード</p>
        </div>
      )}

      {viewMode === 'table' ? (
        <table className="library-table">
          <thead>
            <tr>
              <th>名前</th>
              <th>種類</th>
              <th>更新日時</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {displayDocs.map((doc) => (
              <tr
                key={doc.thread.id}
                className="library-row"
                onClick={() => selectDocument(doc.thread.id)}
                onContextMenu={(e) => handleContextMenu(e, doc)}
                draggable
                onDragStart={(e) => {
                  e.dataTransfer.setData('text/document-id', doc.thread.id);
                }}
              >
                <td className="col-name">
                  <FileText size={16} />
                  <span>{doc.thread.title}</span>
                </td>
                <td className="col-type">{doc.thread.type}</td>
                <td className="col-date">
                  <Clock size={12} />
                  <span>{formatDate(doc.thread.updated_usec)}</span>
                </td>
                <td className="col-actions">
                  <button
                    className="icon-btn icon-btn-sm"
                    onClick={(e) => { e.stopPropagation(); handleContextMenu(e, doc); }}
                  >
                    <MoreVertical size={14} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <div className="library-grid">
          {displayDocs.map((doc) => (
            <div
              key={doc.thread.id}
              className="doc-card"
              onClick={() => selectDocument(doc.thread.id)}
              onContextMenu={(e) => handleContextMenu(e, doc)}
            >
              <div className="doc-card-icon"><FileText size={32} /></div>
              <div className="doc-card-title">{doc.thread.title}</div>
              <div className="doc-card-meta">{formatDate(doc.thread.updated_usec)}</div>
            </div>
          ))}
        </div>
      )}

      {displayDocs.length === 0 && (
        <div className="empty-state-large">
          <FileText size={48} />
          <p>{searchQuery ? '検索結果がありません' : 'ドキュメントがありません'}</p>
          <p className="empty-hint">「新規ドキュメント」ボタンで作成、またはファイルをドラッグ&ドロップ</p>
        </div>
      )}

      {/* Context Menu */}
      {contextMenu && (
        <div className="context-menu" style={{ top: contextMenu.y, left: contextMenu.x }}>
          <button className="context-menu-item" onClick={handleRename}>
            <Edit3 size={14} /> 名前を変更
          </button>
          <button className="context-menu-item danger" onClick={handleDelete}>
            <Trash2 size={14} /> 削除
          </button>
        </div>
      )}
    </div>
  );
}
