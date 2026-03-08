import { useState, useRef } from 'react';
import { Menu, Plus, Search, Home, X, Table, FileText, ChevronDown, LogOut } from 'lucide-react';
import { useDocumentStore } from '../../store/documentStore';
import { authApi, getAuthToken } from '../../api/quipClient';

export function Header() {
  const { toggleSidebar, createDocument, currentUser, searchQuery, search, goHome } = useDocumentStore();
  const [showSearch, setShowSearch] = useState(false);
  const [showCreateMenu, setShowCreateMenu] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleNewDocument = async () => {
    setShowCreateMenu(false);
    const title = prompt('ドキュメント名を入力:');
    if (title) await createDocument(title);
  };

  const handleNewSpreadsheet = async () => {
    setShowCreateMenu(false);
    const title = prompt('スプレッドシート名を入力:');
    if (!title) return;
    const token = getAuthToken();
    const res = await fetch('/api/1/threads/new-spreadsheet', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({ title }),
    });
    if (res.ok) {
      const data = await res.json();
      // Reload and select the new spreadsheet
      await useDocumentStore.getState().loadRecentDocuments();
      await useDocumentStore.getState().selectDocument(data.thread.id);
    }
  };

  const handleSearchToggle = () => {
    setShowSearch(!showSearch);
    if (!showSearch) {
      setTimeout(() => inputRef.current?.focus(), 100);
    } else {
      search('');
    }
  };

  return (
    <header className="header">
      <div className="header-left">
        <button className="icon-btn" onClick={toggleSidebar} title="サイドバー切替">
          <Menu size={20} />
        </button>
        <button className="icon-btn" onClick={goHome} title="ホーム">
          <Home size={18} />
        </button>
        <h1 className="header-title">Quip-SharePoint</h1>
      </div>
      <div className="header-center">
        {showSearch ? (
          <div className="search-bar">
            <Search size={16} />
            <input
              ref={inputRef}
              type="text"
              className="search-input"
              placeholder="ドキュメントを検索..."
              value={searchQuery}
              onChange={(e) => search(e.target.value)}
            />
            <button className="icon-btn icon-btn-sm" onClick={handleSearchToggle}>
              <X size={16} />
            </button>
          </div>
        ) : (
          <>
            <button className="icon-btn" onClick={handleSearchToggle} title="検索">
              <Search size={18} />
            </button>
            <div className="create-menu-wrapper">
              <button className="btn btn-primary" onClick={() => setShowCreateMenu(!showCreateMenu)}>
                <Plus size={16} />
                <span>新規作成</span>
                <ChevronDown size={14} />
              </button>
              {showCreateMenu && (
                <div className="create-dropdown">
                  <button className="create-dropdown-item" onClick={handleNewDocument}>
                    <FileText size={16} /> ドキュメント
                  </button>
                  <button className="create-dropdown-item" onClick={handleNewSpreadsheet}>
                    <Table size={16} /> スプレッドシート
                  </button>
                </div>
              )}
            </div>
          </>
        )}
      </div>
      <div className="header-right">
        {currentUser && (
          <div className="user-badge">
            <span className="user-avatar">{currentUser.name[0]}</span>
            <span className="user-name">{currentUser.name}</span>
            <button className="logout-btn" onClick={authApi.logout} title="ログアウト">
              <LogOut size={14} />
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
