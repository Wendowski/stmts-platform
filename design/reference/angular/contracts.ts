// Illustrative client model. Generate definitive types from versioned OpenAPI.
export type Id = string;
export type MediaState = 'validating'|'uploading'|'processing'|'ready'|'failed';
export interface Author { id: Id; handle: string; displayName: string; avatarUrl?: string; }
export interface Attachment { id: Id; kind: 'image'|'video'; state: MediaState;
  width: number; height: number; alt?: string; decorative: boolean;
  caption?: string; posterUrl?: string; authorizedUrl?: string;
  durationSeconds?: number; transcript?: string; captionsUrl?: string; }
export interface PostSummary { id: Id; author: Author; title?: string; excerpt: string;
  isShort: boolean; readingMinutes: number; publishedAt: string; updatedAt?: string;
  cover?: Attachment; liked: boolean; bookmarked: boolean; reposted: boolean;
  likeCount: number; replyCount: number; repostCount: number; }
export interface Draft { id: Id; revision: number; title: string; summary: string;
  source: string; dialect: 'stmts-md/1'; media: Attachment[]; audience: 'public'; }
export interface Page<T> { items: T[]; nextCursor: string|null; }
export type LoadState<T> = {kind:'loading'} | {kind:'ready';data:T;stale:boolean}
  | {kind:'empty'} | {kind:'error';message:string;requestId?:string};
