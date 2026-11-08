"""stmts-md/1 prototype canonical parser. No generated HTML is consumed by clients."""
import hashlib
import math
import re
from urllib.parse import urlsplit
from markdown_it import MarkdownIt
from mdit_py_plugins.tasklists import tasklists_plugin

class ContentError(ValueError):
    pass

def safe_url(url):
    parts = urlsplit(url)
    return not any(ord(c) < 32 for c in url) and parts.scheme.lower() in ('http', 'https', 'mailto') and (bool(parts.netloc) if parts.scheme.lower() in ('http', 'https') else bool(parts.path))

def parse(source):
    if len(source) > 50000:
        raise ContentError('Body exceeds 50,000 Unicode code points')
    md = MarkdownIt('commonmark', {'html': False, 'maxNesting': 100, 'linkify': False}).enable(['table', 'strikethrough']).use(tasklists_plugin)
    tokens = md.parse(source)
    if max((t.level for t in tokens), default=0) > 12:
        raise ContentError('Nesting exceeds 12')
    errors=[]
    if re.search(r'\]\(\s*(?:javascript|data|file):', source, re.I):
        errors.append('Unsafe link destination')
    count=0
    occurrences={}
    def node(kind, text='', children=None, **attrs):
        nonlocal count
        count+=1
        identity=repr((kind,text,children,attrs))
        digest=hashlib.sha256(identity.encode()).hexdigest()[:20]
        occurrences[digest]=occurrences.get(digest,0)+1
        return dict(id=f'b-{digest}-{occurrences[digest]}',type=kind,text=text,children=children or [],**attrs)
    def inline(items):
        out=[];stack=[out]
        for t in items or []:
            if t.type=='html_inline':
                continue # task-list plugin HTML only; raw HTML is disabled
            if t.type.endswith('_open'):
                kind=t.type[:-5]
                attrs={}
                if kind=='link':
                    url=t.attrGet('href') or ''
                    if safe_url(url): attrs['url']=url
                    else: errors.append('Unsafe link');kind='span'
                n=node({'s':'strike','em':'emphasis'}.get(kind,kind),**attrs);stack[-1].append(n);stack.append(n['children'])
            elif t.type.endswith('_close'):
                if len(stack)>1: stack.pop()
            elif t.type=='image':
                # No media resolution until authorized attachment services exist.
                errors.append('Image requires an authorized ready attachment')
                stack[-1].append(node('text',f"![{t.content}]({t.attrGet('src')})"))
            else:
                stack[-1].append(node('codeInline' if t.type=='code_inline' else 'text', '\n' if t.type in ('softbreak','hardbreak') else t.content))
        return out
    roots=[];stack=[roots]
    mapping={'paragraph':'paragraph','heading':'heading','bullet_list':'list','ordered_list':'orderedList','list_item':'item','blockquote':'quote','table':'table','thead':'tableHead','tbody':'tableBody','tr':'row','th':'headerCell','td':'cell'}
    for t in tokens:
        if t.type=='inline': stack[-1].extend(inline(t.children))
        elif t.type.endswith('_open'):
            k=t.type[:-5];attrs={}
            if k=='heading':attrs['depth']=int(t.tag[1])
            if k=='ordered_list':attrs['start']=int(t.attrGet('start') or 1)
            attrs['sourceSpan']=t.map or [0,0]
            n=node(mapping.get(k,k),**attrs);stack[-1].append(n);stack.append(n['children'])
        elif t.type.endswith('_close'):
            if len(stack)>1:stack.pop()
        elif t.type in ('fence','code_block'):stack[-1].append(node('code',t.content,language=t.info.strip().split(' ')[0],sourceSpan=t.map or [0,0]))
        elif t.type=='hr':stack[-1].append(node('rule',sourceSpan=t.map or [0,0]))
    # Block IDs are assigned after descendants exist; unchanged structures retain IDs.
    seen={}
    def finalize(nodes):
        for n in nodes:
            finalize(n['children'])
            fingerprint={k:v for k,v in n.items() if k not in ('id','sourceSpan')}
            d=hashlib.sha256(repr(fingerprint).encode()).hexdigest()[:20]
            seen[d]=seen.get(d,0)+1;n['id']=f'b-{d}-{seen[d]}'
    finalize(roots)
    blocks=sum(t.type.endswith('_open') or t.type in ('fence','code_block','hr') for t in tokens)
    if blocks>2000:raise ContentError('Document exceeds 2,000 blocks')
    def plain(nodes):
        return ' '.join(n['text']+' '+plain(n['children']) for n in nodes if n['type'] not in ('code','codeInline'))
    text=' '.join(plain(roots).split())
    return dict(dialect='stmts-md/1',blocks=roots,plainText=text,excerpt=text[:280],readingMinutes=max(1,math.ceil(len(text.split())/220)),isShort=len(source)<=500 and all(n['type']=='paragraph' for n in roots),validationErrors=errors)
