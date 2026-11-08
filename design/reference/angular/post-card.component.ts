// Integration example, not a bootstrapped or compiled Angular application.
// Import styles/stmts.css globally. Copy assets to the app's public asset path.
import {ChangeDetectionStrategy, Component, input, output} from '@angular/core';
import {RouterLink} from '@angular/router';
import {PostSummary} from './contracts';
@Component({
  selector: 'stmts-post-card', standalone: true, imports: [RouterLink],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <article class="post-card" [attr.aria-labelledby]="'post-'+post().id">
      <div class="author"><span class="avatar" aria-hidden="true">{{post().author.displayName.slice(0,1)}}</span>
        <a [routerLink]="['/@'+post().author.handle]">{{post().author.displayName}}</a>
        <time [attr.datetime]="post().publishedAt">{{displayDate()}}</time>
      </div>
      <h2 [id]="'post-'+post().id"><a [routerLink]="['/p',post().id]">{{post().title || 'Statement by '+post().author.displayName}}</a></h2>
      <p>{{post().excerpt}}</p>
      @if (!post().isShort) { <a [routerLink]="['/p',post().id]">Continue reading · {{post().readingMinutes}} min</a> }
      <div class="post-actions">
        <button type="button" [attr.aria-pressed]="post().liked" [disabled]="pending()"
          (click)="likeChange.emit(!post().liked)">{{post().liked ? 'Unlike' : 'Like'}} · {{post().likeCount}}</button>
        <a [routerLink]="['/p',post().id]" fragment="replies">Replies · {{post().replyCount}}</a>
        <button type="button" [attr.aria-pressed]="post().bookmarked" [disabled]="pending()"
          (click)="bookmarkChange.emit(!post().bookmarked)">{{post().bookmarked ? 'Remove saved post' : 'Save post'}}</button>
      </div>
    </article>`
})
export class PostCardComponent {
  readonly post = input.required<PostSummary>();
  readonly displayDate = input.required<string>(); // localized by caller
  readonly pending = input(false);
  readonly likeChange = output<boolean>();
  readonly bookmarkChange = output<boolean>();
}
