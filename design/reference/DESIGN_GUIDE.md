# STMTS design guide
Version 1.0 · 8 November 2026 · Proposed implementation baseline

## Product character
STMTS (pronounced “statements”) is a place to publish a thought at its natural length. A quick observation and a considered essay belong to the same network. Markdown is the durable writing format; photos and video support the writing without turning the feed into a video wall.

Design for clarity, authorship, and a reading rhythm. The interface should feel like a well-edited journal with a social layer. Avoid oversized engagement totals, floating reaction confetti, carousel marketing panels in the signed-in feed, decorative gradients, and infinite video autoplay.

## Three concepts
| Direction | Palette and typography | Character | Best use / tradeoff |
|---|---|---|---|
| 01 Paper / Forest — selected | Warm paper #F7F7F2, forest #285C43, Georgia headlines, system UI | Thoughtful, inviting, distinctly editorial | Strong long-form reading; restrained social energy |
| 02 Ink / Signal | White #FFFFFF, ink #171717, cobalt #244ECC, system sans headlines | Crisp, compact, precise | Fast discovery and technical communities; less warmth |
| 03 After Hours | Charcoal #191B22, warm white #F5F0E8, apricot #F0BC92, serif headlines | Intimate, visual, reflective | Creator portfolios and evening reading; heavier atmosphere |

Only Paper / Forest supplies the normative light/dark product tokens. The other concepts are visual explorations, not additional production themes.

## Brand
Use STMTS in uppercase. The speech-page mark suggests both conversation and a written statement. The original outlined wordmark appears in assets/wordmark.svg; use live text for headings and accessible names. Prefer the wordmark in app navigation and the mark in icons or constrained spaces. Do not stretch, bevel, animate, or put the logo in a decorative gradient. Keep the mark optically quieter than the title of the article.

Brand voice: direct, calm, human. “Write a statement,” “Saved to drafts,” “Continue reading.” Error copy explains what happened and the next action: “We couldn’t upload this video. Your text is safe. Try again.” Avoid praise for ordinary actions and fear-based urgency.

## Color and contrast
Semantic tokens allow native and web renderers to share intent. Use ink for text; muted for metadata; line for decorative separators; accent for primary actions, links, and selected state; accent-soft for subdued selection; danger for destructive/error text. Pair accent with on-accent, never a hard-coded white in dark mode. The subtle line token is not an accessible input boundary: fields must receive a darker outline or persistent text labels and sufficient boundary contrast when needed.

Text contrast target: 4.5:1 for normal text, 3:1 for large text and essential graphical controls. Selected tabs use an underline plus weight; errors use explanatory text plus an icon, not just red. Focus ring must contrast at least 3:1 with adjacent colors. Use a 3px ring and 3px offset. Validate real components against every adjacent surface. Never lower text opacity to create secondary text; use the muted token.

## Typography
| Role | Web baseline | Native intent |
|---|---|---|
| Brand / navigation | System sans, 16px, medium | System body / headline |
| Article title | Georgia, 48px/1.1 desktop; 36px compact | Scaled serif large title |
| Feed title | Georgia, 30px/1.15; 26px compact | Scaled serif title2 |
| Reading body | Georgia, 20px/1.7 | Scaled serif body, 20pt/sp baseline |
| UI body | System sans, 16px/1.5 | System body, user scaling enabled |
| Metadata | System sans, 13px/1.5 | Caption with Dynamic Type/font scaling |
| Code | System monospace, 14px/1.6 | Scaled monospace |

No font binaries are required. Georgia is the web preference; use the specified serif fallback if unavailable. iOS uses the system serif design, Android uses the platform serif family. Matching hierarchy and line length matters more than identical glyphs. Do not distribute Apple fonts. Use comfortable word wrapping and language-aware text shaping. Never put fixed heights on text containers. Allow 200% web text enlargement and the largest supported native accessibility sizes; multi-column layouts collapse when text no longer fits.

## Space and geometry
Use the 4/8/12/16/24/32/48/64/96 spacing scale. Cards are mainly separated by whitespace and rules; avoid putting every post in a floating rounded rectangle. Use 10px control corners, 12px media corners, and 16px modal/card corners. Avatars are circular. Buttons are 44px minimum on web/iOS and 48dp on Android, independent of the visible icon size. Use no default card shadows. Reserve a subtle shadow for elevated sheets only.

## Responsive hierarchy
| Available width | Structure | Reading and writing |
|---|---|---|
| <768 CSS px / compact native | Single column, 16px gutters, bottom primary navigation | Full-width content; Write/Preview segmented control |
| 768–1199 CSS px / medium native | 80px navigation rail, 24px gutters, one content column | Reader centered; full-screen composer; no discovery rail |
| ≥1200 CSS px / expanded native | 216px navigation + up to 680px feed + 272px discovery, 24px gaps; shell max 1280px | Reader max 68ch; composer can split source and preview |

Native width classes and available window width own layout decisions, including iPad Split View, Android tablets, and foldables. CSS widths are not device-model detection. Hide the discovery rail before shrinking reading text. Bottom navigation reserves safe-area and keyboard space. In landscape or large text, permit navigation to become a labeled drawer.

## Screen anatomy
Feed: persistent identity and primary navigation, Following/Discover tabs, subtle compose entry, mixed post list, optional topic rail. Following is reverse chronological. Discover is explicitly separate. Long posts show title, an excerpt capped to roughly three lines, reading time, and Continue reading; short posts show the full body up to the short-post threshold. Never cut off inline links or create nested click targets.

Reader: back action with remembered feed position, author/follow, title, summary, optional cover, reading metadata, document body, end-of-article actions, replies. Show a contents menu only for three or more section headings. Do not put a sticky action bar over the last line of content. Reading progress is optional and decorative.

Composer: document title is optional for short posts, source editor, Markdown help, preview switch or split, attachment tray, audience, save state, publish action. The primary action reads Publish; the disabled state has a visible reason. Show revision and error details in the save indicator without stealing focus.

Profile: cover is optional, avatar/name/handle/bio, follow button, counts, Posts/Replies/About tabs. The visual concept shows the Posts tab. Counts are secondary. Own profile exposes Edit profile; other profiles expose Follow and a More menu with mute/block/report.

Media: render cover images in feed at 16:9 with author-controlled crop; reader images preserve original aspect ratio. A gallery uses two equal cells for 2 images and a 2×2 grid for 3–4; the third cell spans width for 3. Tapping opens a navigable lightbox with alt text, caption, close, and position count. Video shows an explicit play button, duration, captions indicator, and controls; no autoplay or automatic sound. Poster frames are images, never fake working video controls in the shipped app.

## Components and states
All interactive components require rest, hover (where available), focus-visible, pressed, selected, disabled, loading, and error states as applicable. A loading button retains width and readable label. Post reaction toggles expose accessible pressed state. Follow uses optimistic state with rollback. Save/bookmark uses “Save post” and “Remove saved post” labels. Destructive delete requires a named confirmation; report opens a reason form and confirms receipt. Use a separate article-title link rather than making an entire card an inaccessible click target.

Empty feed: explain how to follow people and offer Discover people. Empty saved list: “Keep a statement for later.” Offline: persistent banner and cached content with timestamp. Loading: bounded skeletons with a single polite loading announcement, no shimmering under reduced motion. Failed load: retain existing content and offer Retry. Removed post: neutral tombstone, no retained content or media. Content warning: accessible reveal button; hide thumbnail and excerpt until revealed.

## Platform character
Angular: semantic landmarks, real links, keyboard navigation, skip link, native form labels, document title per route. iOS/iPadOS: SwiftUI navigation stack/split view, standard share sheet, system photo picker, system text selection, keyboard shortcuts on iPad. Android: Jetpack Compose navigation, system back/predictive-back integration, system picker/share sheet, 48dp hit targets, fontScale support. Use a native view model and shared typed content schema rather than shipping the web layout in a WebView.

## Motion
120ms hover/pressed; 180ms state transitions; 240ms sheet entry. Animate opacity and modest displacement only. Honor reduced motion, preserve scroll and selection, and never animate an article's body reflow while reading. Motion is not required to understand a state.

## Delivery policy
This is a proposed design baseline, ready for engineering decomposition. Production release still requires device testing, accessibility review, upload/security implementation, and app-store asset preparation. See the normative spec for exact behavior and acceptance gates.
