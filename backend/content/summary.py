"""Visible text and title-aware post classification, independent of source syntax."""
import math
import regex

INLINE = {'text', 'codeInline', 'strong', 'emphasis', 'strike', 'link', 'span'}

def visible_text(nodes):
    parts = []
    for node in nodes:
        if node['type'] in ('code', 'codeInline'):
            continue
        if node['type'] == 'media':
            value = node.get('caption', '')
        else:
            value = node['text'] + visible_text(node['children'])
        parts.append(value if node['type'] in INLINE else value + '\n')
    return ''.join(parts)


def post_summary(source, blocks, *, title=''):
    plain = ' '.join(visible_text(blocks).split())
    excerpt = ''
    for cluster in regex.findall(r'\X', plain):
        if len(excerpt) + len(cluster) > 280:
            break
        excerpt += cluster
    return {'plainText': plain, 'excerpt': excerpt,
            'readingMinutes': max(1, math.ceil(len(plain.split()) / 220)),
            'isShort': not title and len(source) <= 500 and all(n['type'] == 'paragraph' for n in blocks)}
