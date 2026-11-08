"""stmts-md/1 canonical parser; no HTML output or network access."""
from dataclasses import dataclass
import re
from time import monotonic
from urllib.parse import urlsplit
from uuid import UUID

from markdown_it import MarkdownIt
from markdown_it.parser_block import ParserBlock
from markdown_it.parser_inline import ParserInline
from markdown_it.rules_block.state_block import StateBlock
from markdown_it.rules_inline.image import image as image_rule

from .errors import ContentError
from .identity import PreviousTree, assign_ids
from .summary import post_summary

INLINE_TYPES = {'text', 'codeInline', 'strong', 'emphasis', 'strike', 'link', 'span'}

@dataclass(frozen=True)
class Limits:
    source_points: int = 50000
    blocks: int = 2000
    block_depth: int = 12
    total_nodes: int = 20000
    inline_depth: int = 64
    seconds: float = 2.0

class Budget:
    def __init__(self, limits, clock):
        self.limits, self.clock = limits, clock
        self.started = clock()
        self.nodes = self.blocks = 0

    def check(self, span=None):
        if self.clock() - self.started > self.limits.seconds:
            raise ContentError('Content processing time limit exceeded', 'CONTENT_COMPLEXITY_LIMIT', span)

    def node(self, kind, span):
        self.check(span)
        self.nodes += 1
        self.blocks += kind not in INLINE_TYPES
        if self.nodes > self.limits.total_nodes:
            raise ContentError('Content exceeds the node safety limit', 'CONTENT_COMPLEXITY_LIMIT', span)
        if self.blocks > self.limits.blocks:
            raise ContentError('Document exceeds 2,000 blocks', 'CONTENT_BLOCK_LIMIT', span)


def safe_url(url):
    if not isinstance(url, str) or re.search(r'[\x00-\x20\x7f]', url):
        return False
    try:
        parts = urlsplit(url)
        return parts.scheme.lower() in ('http', 'https', 'mailto') and (bool(parts.hostname) if parts.scheme.lower() in ('http', 'https') else bool(parts.path))
    except ValueError:
        return False


def parse(source, *, title='', previous=None, owner_id=None, document_id=None,
          attachment_resolver=None, attachment_manifest=(), limits=None, clock=monotonic, id_allocator=None):
    """previous/resolver must be supplied by trusted domain services, never request JSON.

    Submitted source is never mutated. Spans address logical lines in the LF parsing view.
    Limits are injectable for workers/tests; deployment must also isolate memory/wall time.
    """
    limits = limits or Limits()
    if len(source) > limits.source_points:
        raise ContentError('Body exceeds 50,000 Unicode code points', 'CONTENT_SOURCE_LIMIT')
    if any(0xD800 <= ord(character) <= 0xDFFF or character == '\x00' for character in source):
        raise ContentError('Source contains an invalid or unsupported Unicode scalar', 'CONTENT_UNICODE_INVALID')
    budget = Budget(limits, clock)
    normalized = source.replace('\r\n', '\n').replace('\r', '\n')
    md = MarkdownIt('commonmark', {'html': False, 'maxNesting': 128, 'linkify': False}).enable(['table', 'strikethrough'])

    class GuardedState(StateBlock):
        def push(self, ttype, tag, nesting):
            line = getattr(self, '_stmts_source_line', self.line)
            budget.check([line, line + 1])
            if nesting >= 0 and ttype != 'inline' and self.level + 1 > limits.block_depth:
                raise ContentError('Nesting exceeds 12 block levels', 'CONTENT_DEPTH_LIMIT', [line, line + 1])
            return super().push(ttype, tag, nesting)

    class GuardedBlocks(ParserBlock):
        def parse(self, src, parser, env, tokens):
            if not src:
                return None
            state = GuardedState(src, parser, env, tokens)
            self.tokenize(state, state.line, state.lineMax)
            return state.tokens

    class GuardedInline(ParserInline):
        def skipToken(self, state):
            budget.check()
            if state.level >= limits.inline_depth:
                raise ContentError('Inline nesting exceeds the safety limit', 'CONTENT_COMPLEXITY_LIMIT')
            return super().skipToken(state)
        def tokenize(self, state):
            budget.check()
            if state.level >= limits.inline_depth:
                raise ContentError('Inline nesting exceeds the safety limit', 'CONTENT_COMPLEXITY_LIMIT')
            return super().tokenize(state)

    # Preserve registered extension rules while replacing only state/control boundaries.
    guarded = GuardedBlocks(); guarded.ruler = md.block.ruler; md.block = guarded
    inline_parser = GuardedInline(); inline_parser.ruler = md.inline.ruler; inline_parser.ruler2 = md.inline.ruler2; md.inline = inline_parser
    def remember_start(state, start, end, silent):
        if not silent:
            state._stmts_source_line = start
        return False
    md.block.ruler.before('table', 'stmts_source_boundary', remember_start)
    def record_image_range(state, silent):
        start = state.pos
        matched = image_rule(state, silent)
        if matched and not silent:
            state.tokens[-1].meta['stmtsRange'] = [start, state.pos]
            state.tokens[-1].meta['stmtsLines'] = [state.src[:start].count('\n'), state.src[:state.pos].count('\n') + 1]
        return matched
    md.inline.ruler.at('image', record_image_range)
    tokens = md.parse(normalized)
    errors = []
    if re.search(r'\]\(\s*(?:javascript|data|file):', normalized, re.I):
        errors.append('Unsafe link destination')

    def node(kind, text='', children=None, **attrs):
        budget.node(kind, attrs.get('sourceSpan'))
        return dict(type=kind, text=text, children=children if children is not None else [], **attrs)

    manifest = set()
    for identity in attachment_manifest:
        if not isinstance(identity, str) or not re.fullmatch(r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}', identity):
            raise ContentError('Attachment manifest has an invalid identity', 'CONTENT_MEDIA_INVALID')
        manifest.add(str(UUID(identity)))
    if len(manifest) > 4:
        raise ContentError('A post supports at most four images or one video', 'CONTENT_MEDIA_LIMIT')
    resolved = {}
    def resolve(asset_id):
        if asset_id not in resolved:
            resolved[asset_id] = attachment_resolver(asset_id) if attachment_resolver and asset_id in manifest else None
        asset = resolved[asset_id]
        if not asset or asset.attachment_id != asset_id or not asset.eligible or asset.state != 'ready':
            return None
        if len(asset.alt) > 1000 or len(asset.caption) > 500 or (asset.kind == 'image' and not asset.decorative and not asset.alt.strip()):
            return None
        return asset

    def media(asset, span):
        return node('media', sourceSpan=span, attachmentId=asset.attachment_id, mediaType=asset.kind,
                    alt=asset.alt, decorative=asset.decorative, caption=asset.caption)

    media_offsets, paragraph_sources = {}, {}

    def inline(items, span, allow_media):
        out, stack = [], []
        released_paragraph = False
        stack.append(out)
        for token in items or []:
            budget.check(span)
            if token.type.endswith('_open'):
                kind = {'s': 'strike', 'em': 'emphasis'}.get(token.type[:-5], token.type[:-5])
                attrs = {}
                if kind == 'link':
                    url = token.attrGet('href') or ''
                    if safe_url(url): attrs['url'] = url
                    else: errors.append('Unsafe link'); kind = 'span'
                if len(stack) >= limits.inline_depth:
                    raise ContentError('Inline nesting exceeds the safety limit', 'CONTENT_COMPLEXITY_LIMIT', span)
                item = node(kind, **attrs); stack[-1].append(item); stack.append(item['children'])
            elif token.type.endswith('_close'):
                if len(stack) > 1: stack.pop()
            elif token.type == 'image':
                src = token.attrGet('src') or ''
                match = re.fullmatch(r'stmts-media:([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})', src)
                asset = resolve(str(UUID(match[1]))) if match else None
                if asset and asset.kind == 'image' and allow_media and len(stack) == 1:
                    if not released_paragraph:
                        budget.blocks -= 1  # The temporary paragraph is replaced by media/text blocks.
                        released_paragraph = True
                    relative = token.meta['stmtsLines']
                    placement = media(asset, [span[0] + relative[0], span[0] + relative[1]])
                    media_offsets[id(placement)] = token.meta['stmtsRange']
                    stack[-1].append(placement)
                else:
                    errors.append('Image requires an authorized ready attachment')
                    stack[-1].append(node('text', f'![{token.content}]({src})'))
            elif token.type == 'html_inline':
                # HTML is disabled; no plugin-generated HTML is consumed.
                stack[-1].append(node('text', token.content))
            else:
                stack[-1].append(node('codeInline' if token.type == 'code_inline' else 'text', '\n' if token.type in ('softbreak', 'hardbreak') else token.content))
        return out

    roots, parents = [], []
    stack = [roots]
    mapping = {'paragraph': 'paragraph', 'heading': 'heading', 'bullet_list': 'list', 'ordered_list': 'orderedList', 'list_item': 'item', 'blockquote': 'quote', 'table': 'table', 'thead': 'tableHead', 'tbody': 'tableBody', 'tr': 'row', 'th': 'headerCell', 'td': 'cell'}
    for token in tokens:
        budget.check(token.map)
        if token.type == 'inline':
            if parents and 'sourceSpan' not in parents[-1] and token.map:
                parents[-1]['sourceSpan'] = token.map[:]
            paragraph_sources[id(parents[-1])] = token.content
            items = token.children or []
            # Recognize the unescaped source marker only in the first paragraph of an item.
            task = re.match(r'^\[([ xX])\](?:[ \t]+|$)', token.content)
            if task and len(parents) >= 2 and parents[-1]['type'] == 'paragraph' and parents[-2]['type'] == 'item' and parents[-2]['children'][0] is parents[-1]:
                parents[-2]['type'] = 'taskItem'; parents[-2]['checked'] = task[1].lower() == 'x'
                if items and items[0].type == 'text':
                    items[0].content = items[0].content[task.end():]
            stack[-1].extend(inline(items, token.map, parents[-1]['type'] == 'paragraph'))
        elif token.type.endswith('_open'):
            key = token.type[:-5]; attrs = {}
            if key == 'heading': attrs['depth'] = int(token.tag[1])
            if key == 'ordered_list': attrs['start'] = int(token.attrGet('start') or 1)
            if token.map is not None: attrs['sourceSpan'] = token.map[:]
            item = node(mapping[key], **attrs); stack[-1].append(item); stack.append(item['children']); parents.append(item)
        elif token.type.endswith('_close'):
            stack.pop(); parents.pop()
        elif token.type in ('fence', 'code_block'):
            stack[-1].append(node('code', token.content, language=token.info.strip().split(' ')[0], sourceSpan=token.map[:]))
        elif token.type == 'hr':
            stack[-1].append(node('rule', sourceSpan=token.map[:]))

    def normalize_blocks(nodes):
        result = []
        for item in nodes:
            if item['type'] not in INLINE_TYPES:
                # Paragraph inline media becomes block-level placements without changing the schema.
                if item['type'] == 'paragraph' and any(child['type'] == 'media' for child in item['children']):
                    children = []
                    raw = paragraph_sources[id(item)]
                    offset = 0
                    def segment_span(start, end):
                        region = raw[start:end]
                        if not region.strip():
                            return None
                        left = start + len(region) - len(region.lstrip())
                        right = end - (len(region) - len(region.rstrip()))
                        base = item['sourceSpan'][0]
                        return [base + raw[:left].count('\n'), base + raw[:right].count('\n') + 1]
                    for child in item['children']:
                        if child['type'] == 'media':
                            start, end = media_offsets[id(child)]
                            text_range = segment_span(offset, start)
                            if children and text_range:
                                result.append(node('paragraph', children=children, sourceSpan=text_range))
                            children = []
                            offset = end
                            result.append(child)
                        else:
                            children.append(child)
                    text_range = segment_span(offset, len(raw))
                    if children and text_range:
                        result.append(node('paragraph', children=children, sourceSpan=text_range))
                    continue
                item['children'] = normalize_blocks(item['children'])
                if 'sourceSpan' not in item:
                    spans = [child['sourceSpan'] for child in item['children'] if 'sourceSpan' in child]
                    if not spans:
                        raise ContentError('Unable to determine a source line range', 'CONTENT_SPAN_INVALID')
                    item['sourceSpan'] = [min(s[0] for s in spans), max(s[1] for s in spans)]
            result.append(item)
        return result
    roots = normalize_blocks(roots)
    assets = [resolve(asset_id) for asset_id in sorted(manifest)]
    if any(asset is None or asset.kind not in ('image', 'video') for asset in assets):
        errors.append('Attachment manifest contains unavailable media')
    available = [asset for asset in assets if asset]
    if any(asset.kind == 'video' for asset in available) and len(manifest) != 1:
        errors.append('A post supports up to four images or one video, not both')
    # Unreferenced attachments remain a domain-level attachment area, not fabricated source spans.
    # Parsing validates them; the post media manifest controls their separate rendering.
    def validate_tree(nodes, depth=0):
        for item in nodes:
            budget.check(item.get('sourceSpan'))
            if item['type'] not in INLINE_TYPES:
                span = item.get('sourceSpan')
                line_count = normalized.count('\n') + bool(normalized and not normalized.endswith('\n'))
                if not span or not 0 <= span[0] < span[1] <= line_count:
                    raise ContentError('Unable to determine a valid source line range', 'CONTENT_SPAN_INVALID')
            current = depth + (item['type'] not in INLINE_TYPES)
            if current > limits.block_depth:
                raise ContentError('Nesting exceeds 12 block levels', 'CONTENT_DEPTH_LIMIT', item.get('sourceSpan'))
            validate_tree(item['children'], current)
    validate_tree(roots)
    assign_ids(roots, previous, owner_id=owner_id, document_id=document_id, allocator=id_allocator)
    budget.check()
    return dict(dialect='stmts-md/1', blocks=roots, **post_summary(source, roots, title=title), validationErrors=errors)
