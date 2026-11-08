"""Bounded order-preserving reconciliation of document-local opaque IDs."""
from bisect import bisect_left
from collections import Counter
from dataclasses import dataclass
import hashlib
import json
from uuid import uuid4
from .errors import ContentError

@dataclass(frozen=True)
class PreviousTree:
    owner_id: str
    document_id: str
    blocks: list

STRUCTURAL = {'list', 'orderedList', 'item', 'taskItem', 'quote', 'table', 'tableHead', 'tableBody', 'row', 'cell', 'headerCell'}


def assign_ids(blocks, previous=None, *, owner_id=None, document_id=None, allocator=None):
    if previous is not None and (not owner_id or not document_id or previous.owner_id != owner_id or previous.document_id != document_id):
        raise ContentError('Previous content belongs to another document', 'CONTENT_IDENTITY_SCOPE')
    allocate = allocator or (lambda: str(uuid4()))
    hashes = {}
    old_ids = set()
    def fingerprint(node, old=False, depth=0):
        if depth > 80 or len(hashes) >= 40000:
            raise ContentError('Previous content exceeds reconciliation limits', 'CONTENT_COMPLEXITY_LIMIT')
        children = [fingerprint(child, old, depth + 1) for child in node['children']]
        attrs = {key: value for key, value in node.items() if key not in ('id', 'sourceSpan', 'children')}
        value = hashlib.sha256(json.dumps([attrs, children], sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        hashes[id(node)] = value
        if old:
            identity = node.get('id')
            if not isinstance(identity, str) or not identity or identity in old_ids:
                raise ContentError('Previous content has invalid identities', 'CONTENT_IDENTITY_INVALID')
            old_ids.add(identity)
        return value
    for node in blocks:
        fingerprint(node)
    old = previous.blocks if previous else []
    for node in old:
        fingerprint(node, True)
    used = set()
    def new_id():
        for _ in range(32):
            value = allocate()
            if isinstance(value, str) and value and len(value) <= 128 and value not in used and value not in old_ids:
                used.add(value)
                return value
        raise ContentError('Unable to allocate a unique content identity', 'CONTENT_IDENTITY_INVALID')
    def anchors(a, b):
        ac = Counter(hashes[id(n)] for n in a)
        bc = Counter(hashes[id(n)] for n in b)
        positions = {hashes[id(n)]: i for i, n in enumerate(a) if ac[hashes[id(n)]] == 1}
        pairs = [(positions[hashes[id(n)]], j) for j, n in enumerate(b) if bc[hashes[id(n)]] == 1 and hashes[id(n)] in positions]
        # Longest increasing subsequence of old positions: O(n log n).
        tails, indices, parents = [], [], []
        for i, (pos, _) in enumerate(pairs):
            k = bisect_left(tails, pos)
            parents.append(indices[k - 1] if k else -1)
            if k == len(tails): tails.append(pos); indices.append(i)
            else: tails[k] = pos; indices[k] = i
        out = []
        index = indices[-1] if indices else -1
        while index >= 0:
            out.append(pairs[index]); index = parents[index]
        return out[::-1]
    def gap(a, b):
        if [hashes[id(n)] for n in a] == [hashes[id(n)] for n in b]:
            return {j: n for j, n in enumerate(a)}
        # Only unique structural containers in the bounded gap are eligible.
        ac, bc = Counter(n['type'] for n in a), Counter(n['type'] for n in b)
        positions = {n['type']: (i, n) for i, n in enumerate(a) if n['type'] in STRUCTURAL and ac[n['type']] == 1}
        mapping, last = {}, -1
        for j, node in enumerate(b):
            candidate = positions.get(node['type'])
            if candidate and bc[node['type']] == 1 and candidate[0] > last:
                last, mapping[j] = candidate
        return mapping
    def reconcile(a, b):
        if [hashes[id(n)] for n in a] == [hashes[id(n)] for n in b]:
            matches = dict(enumerate(a))
        else:
            matches, ai, bi = {}, 0, 0
            for ax, bx in anchors(a, b) + [(len(a), len(b))]:
                matches.update({bi + j: n for j, n in gap(a[ai:ax], b[bi:bx]).items()})
                if bx < len(b): matches[bx] = a[ax]
                ai, bi = ax + 1, bx + 1
        for j, node in enumerate(b):
            prior = matches.get(j)
            if prior is not None:
                identity = prior['id']
                if identity in used:
                    raise ContentError('Content identity was reused', 'CONTENT_IDENTITY_INVALID')
                node['id'] = identity; used.add(identity)
            else:
                node['id'] = new_id()
            reconcile(prior['children'] if prior else [], node['children'])
    reconcile(old, blocks)
