import { create } from 'zustand';
import type { QuipThread, QuipFolder, QuipUser } from '../types';
import { quipApi } from '../api/quipClient';

interface DocumentStore {
  // State
  documents: QuipThread[];
  folders: QuipFolder[];
  currentDocument: QuipThread | null;
  currentFolder: QuipFolder | null;
  currentUser: QuipUser | null;
  sidebarOpen: boolean;
  loading: boolean;
  searchQuery: string;
  searchResults: QuipThread[];
  view: 'library' | 'editor';

  // Actions
  loadRecentDocuments: () => Promise<void>;
  loadFolders: (parentId?: string) => Promise<void>;
  selectDocument: (id: string) => Promise<void>;
  selectFolder: (id: string) => Promise<void>;
  createDocument: (title: string, folderId?: string) => Promise<QuipThread>;
  createFolder: (title: string, parentId?: string) => Promise<void>;
  saveDocument: (id: string, content: string, title?: string) => Promise<void>;
  deleteDocument: (id: string) => Promise<void>;
  renameDocument: (id: string, title: string) => Promise<void>;
  moveDocument: (id: string, folderId: string) => Promise<void>;
  loadCurrentUser: () => Promise<void>;
  toggleSidebar: () => void;
  clearCurrentDocument: () => void;
  setSearchQuery: (q: string) => void;
  search: (q: string) => Promise<void>;
  goHome: () => void;
}

export const useDocumentStore = create<DocumentStore>((set, get) => ({
  documents: [],
  folders: [],
  currentDocument: null,
  currentFolder: null,
  currentUser: null,
  sidebarOpen: true,
  loading: false,
  searchQuery: '',
  searchResults: [],
  view: 'library',

  loadRecentDocuments: async () => {
    set({ loading: true });
    const documents = await quipApi.getRecentThreads();
    set({ documents, loading: false });
  },

  loadFolders: async (parentId?: string) => {
    const folders = await quipApi.getFolders(parentId);
    set({ folders });
  },

  selectDocument: async (id: string) => {
    set({ loading: true, view: 'editor' });
    const currentDocument = await quipApi.getThread(id);
    set({ currentDocument, loading: false });
  },

  selectFolder: async (id: string) => {
    const currentFolder = await quipApi.getFolder(id);
    set({ currentFolder, currentDocument: null, view: 'library' });
    // Reload folder documents
    await get().loadRecentDocuments();
  },

  createDocument: async (title: string, folderId?: string) => {
    const doc = await quipApi.createDocument(title, '', folderId);
    await get().loadRecentDocuments();
    set({ currentDocument: doc, view: 'editor' });
    return doc;
  },

  createFolder: async (title: string, parentId?: string) => {
    await quipApi.createFolder(title, parentId);
    await get().loadFolders(parentId);
  },

  saveDocument: async (id: string, content: string, title?: string) => {
    const doc = await quipApi.editDocument(id, content, title);
    set({ currentDocument: doc });
  },

  deleteDocument: async (id: string) => {
    await quipApi.deleteThread(id);
    set({ currentDocument: null, view: 'library' });
    await get().loadRecentDocuments();
  },

  renameDocument: async (id: string, title: string) => {
    const doc = await quipApi.editDocument(id, undefined, title);
    set({ currentDocument: doc });
    await get().loadRecentDocuments();
  },

  moveDocument: async (id: string, _folderId: string) => {
    await quipApi.editDocument(id, undefined, undefined);
    await get().loadRecentDocuments();
  },

  loadCurrentUser: async () => {
    const currentUser = await quipApi.getCurrentUser();
    set({ currentUser });
  },

  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
  clearCurrentDocument: () => set({ currentDocument: null, view: 'library' }),

  setSearchQuery: (searchQuery: string) => set({ searchQuery }),

  search: async (q: string) => {
    set({ searchQuery: q });
    if (!q.trim()) {
      set({ searchResults: [] });
      return;
    }
    // Client-side search over loaded documents
    const docs = get().documents;
    const results = docs.filter(d =>
      d.thread.title.toLowerCase().includes(q.toLowerCase()) ||
      d.html.toLowerCase().includes(q.toLowerCase())
    );
    set({ searchResults: results });
  },

  goHome: () => set({ currentDocument: null, currentFolder: null, view: 'library', searchQuery: '', searchResults: [] }),
}));
