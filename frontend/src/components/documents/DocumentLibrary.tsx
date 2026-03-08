import { FileText, Clock } from 'lucide-react';
import { useDocumentStore } from '../../store/documentStore';

export function DocumentLibrary() {
  const { documents, selectDocument, loading } = useDocumentStore();

  if (loading) {
    return <div className="loading">読み込み中...</div>;
  }

  return (
    <div className="document-library">
      <div className="library-header">
        <h2>ドキュメントライブラリ</h2>
      </div>
      <table className="library-table">
        <thead>
          <tr>
            <th>名前</th>
            <th>種類</th>
            <th>更新日時</th>
          </tr>
        </thead>
        <tbody>
          {documents.map((doc) => (
            <tr
              key={doc.thread.id}
              className="library-row"
              onClick={() => selectDocument(doc.thread.id)}
            >
              <td className="col-name">
                <FileText size={16} />
                <span>{doc.thread.title}</span>
              </td>
              <td className="col-type">{doc.thread.type}</td>
              <td className="col-date">
                <Clock size={12} />
                <span>
                  {new Date(doc.thread.updated_usec / 1000).toLocaleString('ja-JP')}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {documents.length === 0 && (
        <div className="empty-state-large">
          <FileText size={48} />
          <p>ドキュメントがありません</p>
          <p className="empty-hint">「新規ドキュメント」ボタンで作成してください</p>
        </div>
      )}
    </div>
  );
}
