import { Menu, Plus } from 'lucide-react';
import { useDocumentStore } from '../../store/documentStore';

export function Header() {
  const { toggleSidebar, createDocument, currentUser } = useDocumentStore();

  const handleNewDocument = async () => {
    const title = prompt('ドキュメント名を入力:');
    if (title) await createDocument(title);
  };

  return (
    <header className="header">
      <div className="header-left">
        <button className="icon-btn" onClick={toggleSidebar} title="Toggle sidebar">
          <Menu size={20} />
        </button>
        <h1 className="header-title">Quip-SharePoint</h1>
      </div>
      <div className="header-center">
        <button className="btn btn-primary" onClick={handleNewDocument}>
          <Plus size={16} />
          <span>新規ドキュメント</span>
        </button>
      </div>
      <div className="header-right">
        {currentUser && <span className="user-name">{currentUser.name}</span>}
      </div>
    </header>
  );
}
