import type { QuipThread, QuipFolder, QuipMessage, QuipUser } from '../types';

const BASE = '/api/1';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export const quipApi = {
  // Threads
  getRecentThreads: (count = 50) =>
    request<QuipThread[]>(`/threads/recent?count=${count}`),

  getThread: (id: string) =>
    request<QuipThread>(`/threads/${id}`),

  createDocument: (title: string, content = '', folderId?: string) =>
    request<QuipThread>('/threads/new-document', {
      method: 'POST',
      body: JSON.stringify({ title, content, folder_id: folderId }),
    }),

  editDocument: (threadId: string, content?: string, title?: string) =>
    request<QuipThread>('/threads/edit-document', {
      method: 'POST',
      body: JSON.stringify({ thread_id: threadId, content, title }),
    }),

  deleteThread: (id: string) =>
    request<{ ok: boolean }>(`/threads/${id}/delete`, { method: 'POST' }),

  // Folders
  getFolders: (parentId?: string) =>
    request<QuipFolder[]>(`/folders${parentId ? `?parent_id=${parentId}` : ''}`),

  getFolder: (id: string) =>
    request<QuipFolder>(`/folders/${id}`),

  createFolder: (title: string, parentId?: string, color = 'manila') =>
    request<QuipFolder>('/folders/new', {
      method: 'POST',
      body: JSON.stringify({ title, parent_id: parentId, color }),
    }),

  updateFolder: (folderId: string, title?: string, color?: string) =>
    request<QuipFolder>('/folders/update', {
      method: 'POST',
      body: JSON.stringify({ folder_id: folderId, title, color }),
    }),

  // Messages
  getMessages: (threadId: string) =>
    request<QuipMessage[]>(`/messages/${threadId}`),

  postMessage: (threadId: string, content: string) =>
    request<QuipMessage>('/messages/new', {
      method: 'POST',
      body: JSON.stringify({ thread_id: threadId, content }),
    }),

  // Users
  getCurrentUser: () => request<QuipUser>('/users/current'),
  getUser: (id: string) => request<QuipUser>(`/users/${id}`),
};
