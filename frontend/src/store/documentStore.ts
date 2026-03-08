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

  // Actions
  loadRecentDocuments: () => Promise<void>;
  loadFolders: (parentId?: string) => Promise<void>;
  selectDocument: (id: string) => Promise<void>;
  selectFolder: (id: string) => Promise<void>;
  createDocument: (title: string, folderId?: string) => Promise<QuipThread>;
  createFolder: (title: string, parentId?: string) => Promise<void>;
  saveDocument: (id: string, content: string, title?: string) => Promise<void>;
  deleteDocument: (id: string) => Promise<void>;
  loadCurrentUser: () => Promise<void>;
  toggleSidebar: () => void;
  clearCurrentDocument: () => void;
}

export const useDocumentStore = create<DocumentStore>((set, get) => ({
  documents: [],
  folders: [],
  currentDocument: null,
  currentFolder: null,
  currentUser: null,
  sidebarOpen: true,
  loading: false,

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
    set({ loading: true });
    const currentDocument = await quipApi.getThread(id);
    set({ currentDocument, loading: false });
  },

  selectFolder: async (id: string) => {
    const currentFolder = await quipApi.getFolder(id);
    set({ currentFolder });
  },

  createDocument: async (title: string, folderId?: string) => {
    const doc = await quipApi.createDocument(title, '', folderId);
    await get().loadRecentDocuments();
    set({ currentDocument: doc });
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
    set({ currentDocument: null });
    await get().loadRecentDocuments();
  },

  loadCurrentUser: async () => {
    const currentUser = await quipApi.getCurrentUser();
    set({ currentUser });
  },

  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
  clearCurrentDocument: () => set({ currentDocument: null }),
}));
