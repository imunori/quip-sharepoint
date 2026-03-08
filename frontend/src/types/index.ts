export interface QuipThread {
  thread: {
    id: string;
    title: string;
    type: string;
    link: string;
    created_usec: number;
    updated_usec: number;
    author_id: string;
    sharing: { folder_ids: string[] };
  };
  html: string;
}

export interface QuipFolder {
  folder: {
    id: string;
    title: string;
    color: string;
    parent_id: string | null;
    creator_id: string;
    created_usec: number;
    updated_usec: number;
  };
  member_ids: string[];
  children: Array<{ folder_id?: string; thread_id?: string }>;
}

export interface QuipMessage {
  id: string;
  author_id: string;
  text: string;
  annotation_id: string | null;
  created_usec: number;
}

export interface QuipUser {
  id: string;
  name: string;
  emails: string[];
  profile_picture_url: string;
}
