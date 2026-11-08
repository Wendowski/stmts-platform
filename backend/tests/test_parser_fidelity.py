from dataclasses import replace
import json

import pytest
from jsonschema import Draft202012Validator

from content.attachments import Attachment
from content.errors import ContentError
from content.identity import PreviousTree
from content.parser import Limits, parse
from test_content_contract import normalize, ROOT, SCHEMA


def walk(nodes):
    for node in nodes:
        yield node
        yield from walk(node['children'])


def revision(source, old):
    return parse(source, owner_id='owner', document_id='document', previous=PreviousTree('owner', 'document', old['blocks']))


@pytest.mark.parametrize('size', [49999, 50000, 50001])
def test_exact_source_boundary(size):
    if size > 50000:
        with pytest.raises(ContentError) as exc: parse('a' * size)
        assert exc.value.code == 'CONTENT_SOURCE_LIMIT'
    else:
        assert parse('a' * size)['plainText'] == 'a' * size


@pytest.mark.parametrize('size', [1999, 2000, 2001])
def test_exact_block_boundary(size):
    source = '\n\n'.join('word' for _ in range(size))
    if size > 2000:
        with pytest.raises(ContentError) as exc: parse(source)
        assert exc.value.code == 'CONTENT_BLOCK_LIMIT'
    else:
        assert len(parse(source)['blocks']) == size


@pytest.mark.parametrize('depth', [11, 12, 13])
def test_exact_block_depth_boundary(depth):
    source = '> ' * (depth - 1) + 'word'
    if depth > 12:
        with pytest.raises(ContentError) as exc: parse(source)
        assert exc.value.code == 'CONTENT_DEPTH_LIMIT'
    else:
        assert len(list(walk(parse(source)['blocks']))) == depth + 1  # one text leaf


@pytest.mark.parametrize('newline', ['\n', '\r\n', '\r'])
def test_normalized_line_spans_and_semantics(newline):
    source = 'alpha\n\nbeta\n'.replace('\n', newline)
    parsed = parse(source)
    assert [node['sourceSpan'] for node in parsed['blocks']] == [[0, 1], [2, 3]]
    assert normalize(parsed) == normalize(parse('alpha\n\nbeta\n'))


@pytest.mark.parametrize('source', [
    '| A | B |\n| --- | --- |\n| 1 | 2 |',
    '> first\n>\n> - nested\n>   - deeper',
    '```python\nnot closed\n',
    'first\n\n```\ncode\n```\n',
])
def test_spans_are_nonempty_and_contain_descendants(source):
    doc = parse(source)
    line_count = len(source.splitlines())
    def verify(nodes, outer=None):
        for node in nodes:
            span = node.get('sourceSpan')
            if span:
                assert 0 <= span[0] < span[1] <= line_count
                if outer: assert outer[0] <= span[0] < span[1] <= outer[1]
            verify(node['children'], span or outer)
    verify(doc['blocks'])
    Draft202012Validator(SCHEMA).validate(doc)


def test_table_cells_and_unclosed_fence_ranges():
    table = parse('before\n\n| A | B |\n| --- | --- |\n| 1 | 2 |')['blocks'][1]
    assert [node['sourceSpan'] for node in walk([table]) if node['type'] in ('headerCell', 'cell')] == [[2, 3], [2, 3], [4, 5], [4, 5]]
    assert parse('```\nopen')['blocks'][0]['sourceSpan'] == [0, 2]


@pytest.mark.parametrize('source', ['\ud800', '\udfff', '\x00'])
def test_invalid_scalars_are_rejected_not_replaced(source):
    with pytest.raises(ContentError) as exc: parse(source)
    assert exc.value.code == 'CONTENT_UNICODE_INVALID'


def test_original_codepoint_limit_precedes_newline_normalization():
    with pytest.raises(ContentError): parse('\r\n' * 25001)


def test_unicode_composition_bidi_and_emoji_remain_unchanged():
    source = 'cafe\u0301 👨‍👩‍👧‍👦 你好 مرحبًا'
    assert parse(source)['blocks'][0]['children'][0]['text'] == source


def test_task_states_and_nested_formatting():
    doc = parse('- [X] **Read** [guide](https://example.com)\n  - [ ] Nested\n- ordinary')
    tasks = [node for node in walk(doc['blocks']) if node['type'] == 'taskItem']
    assert [node['checked'] for node in tasks] == [True, False]
    assert any(node['type'] == 'strong' for node in walk(tasks[0]['children']))
    assert any(node['type'] == 'link' for node in walk(tasks[0]['children']))
    Draft202012Validator(SCHEMA).validate(doc)


@pytest.mark.parametrize('source', ['[x] ordinary', '- \\[x] escaped', '```\n- [x] code\n```', '- `[x]` code', '- first\n\n  [x] second paragraph'])
def test_task_markers_only_in_valid_source_positions(source):
    assert not any(node['type'] == 'taskItem' for node in walk(parse(source)['blocks']))


def test_defensive_node_time_and_inline_limits():
    with pytest.raises(ContentError) as exc: parse('**bold** *italic*', limits=Limits(total_nodes=3))
    assert exc.value.code == 'CONTENT_COMPLEXITY_LIMIT'
    times = iter([0, 10])
    with pytest.raises(ContentError) as exc: parse('word', clock=lambda: next(times))
    assert exc.value.code == 'CONTENT_COMPLEXITY_LIMIT'
    with pytest.raises(ContentError): parse('**a *b* c**', limits=Limits(inline_depth=2))


def test_table_nodes_count_toward_block_budget():
    # table + head + row + 2 header cells + body + row + 2 cells = 9.
    source = '| A | B |\n| --- | --- |\n| 1 | 2 |'
    assert parse(source, limits=Limits(blocks=9))
    with pytest.raises(ContentError): parse(source, limits=Limits(blocks=8))


def test_pathological_nesting_is_rejected_without_flattening():
    with pytest.raises(ContentError) as exc: parse('> ' * 1000 + 'tail')
    assert exc.value.code == 'CONTENT_DEPTH_LIMIT'


def test_ids_are_fresh_on_first_parse_and_scoped_for_revision():
    old = parse('first\n\n# Anchor')
    assert old['blocks'][0]['id'] != parse('first\n\n# Anchor')['blocks'][0]['id']
    new = revision('new\n\nfirst\n\n# Anchor', old)
    assert [node['id'] for node in new['blocks'][1:]] == [node['id'] for node in old['blocks']]
    with pytest.raises(ContentError):
        parse('first', previous=PreviousTree('foreign', 'document', old['blocks']), owner_id='owner', document_id='document')


def test_reparse_reuses_all_ids_and_child_edits_preserve_container_and_siblings():
    source = '- first\n- second\n\n# Anchor'
    old = parse(source)
    assert revision(source, old)['blocks'] == old['blocks']
    new = revision('- changed\n- second\n\n# Anchor', old)
    assert new['blocks'][0]['id'] == old['blocks'][0]['id']
    assert new['blocks'][0]['children'][1]['id'] == old['blocks'][0]['children'][1]['id']
    assert new['blocks'][1]['id'] == old['blocks'][1]['id']


@pytest.mark.parametrize('changed', ['# Start\n\nsame\n\nsame\n\nsame\n\n# End', '# Start\n\nsame\n\n# End'])
def test_ambiguous_duplicates_get_fresh_ids_with_surrounding_anchors(changed):
    old = parse('# Start\n\nsame\n\nsame\n\n# End')
    new = revision(changed, old)
    assert new['blocks'][0]['id'] == old['blocks'][0]['id']
    assert new['blocks'][-1]['id'] == old['blocks'][-1]['id']
    assert not {node['id'] for node in new['blocks'][1:-1]} & {node['id'] for node in old['blocks'][1:-1]}
    ids = [node['id'] for node in walk(new['blocks'])]
    assert len(ids) == len(set(ids))


def test_repeated_content_reconciliation_is_bounded():
    old = parse('\n\n'.join(['same'] * 1000))
    new = revision('\n\n'.join(['same'] * 1001), old)
    assert len(new['blocks']) == 1001
    assert not {node['id'] for node in new['blocks']} & {node['id'] for node in old['blocks']}


ASSET_ID = '11111111-1111-4111-8111-111111111111'
READY = Attachment(ASSET_ID, True, 'image', 'ready', alt='Green hills')


def test_authorized_media_placements_and_manifest_are_distinct():
    calls = []
    def resolver(identity): calls.append(identity); return READY
    doc = parse('\n\n'.join([f'![hills](stmts-media:{ASSET_ID})'] * 4), attachment_manifest=[ASSET_ID] * 4, attachment_resolver=resolver)
    assert [node['type'] for node in doc['blocks']] == ['media'] * 4
    assert calls == [ASSET_ID]
    Draft202012Validator(SCHEMA).validate(doc)


@pytest.mark.parametrize('asset', [None, replace(READY, eligible=False), replace(READY, state='processing'), replace(READY, state='quarantined'), replace(READY, kind='video'), replace(READY, alt='')])
def test_unavailable_or_ineligible_media_never_exposes_delivery_urls(asset):
    doc = parse(f'![hills](stmts-media:{ASSET_ID})', attachment_manifest=[ASSET_ID], attachment_resolver=lambda _: asset)
    assert doc['validationErrors']
    assert not any(node['type'] == 'media' for node in walk(doc['blocks']))
    assert 'https://' not in json.dumps(doc)


@pytest.mark.parametrize('url', ['https://example.com/image.png', 'data:image/svg+xml,x', 'stmts-media:not-a-uuid', 'stmts-media://'+ASSET_ID])
def test_malformed_schemes_do_not_reach_resolver(url):
    calls = []
    doc = parse(f'![x]({url})', attachment_manifest=[ASSET_ID], attachment_resolver=lambda x: calls.append(x))
    # The explicit manifest itself is validated, but no malformed source reaches resolution.
    assert calls == [ASSET_ID]
    assert not any(node['type'] == 'media' for node in walk(doc['blocks']))
    assert doc['validationErrors']


def test_source_uuid_alone_does_not_grant_access():
    calls = []
    doc = parse(f'![hills](stmts-media:{ASSET_ID})', attachment_resolver=lambda x: calls.append(x) or READY)
    assert calls == []
    assert doc['validationErrors']


def test_summary_is_title_aware_and_preserves_inline_spacing():
    assert not parse('short', title='Title')['isShort']
    assert parse('a**b**c [d](https://example.com).')['plainText'] == 'abc d.'
    assert parse('- [x] words\n\n| A | B |\n| --- | --- |\n| 1 | 2 |')['plainText'] == 'words A B 1 2'
    assert parse('```\n' + 'code ' * 1000 + '\n```')['readingMinutes'] == 1


@pytest.mark.parametrize('cluster', ['e\u0301', '👨‍👩‍👧‍👦'])
def test_excerpt_ends_before_a_partial_grapheme(cluster):
    assert parse('x' * 279 + cluster)['excerpt'] == 'x' * 279


def test_structured_failures_map_to_422_without_source():
    from content.http import content_error_response
    try:
        parse('> ' * 12 + 'private-source-value')
    except ContentError as error:
        response = content_error_response(error, 'request-1')
    assert response.status_code == 422
    assert response.data['code'] == 'CONTENT_DEPTH_LIMIT'
    assert response.data['fieldErrors']['body'][0]['sourceSpan'] == [0, 1]
    assert 'private-source-value' not in json.dumps(response.data)


def test_isolated_worker_success_and_deadline():
    from content.worker import parse_isolated
    assert parse_isolated('a **clear** thought')['plainText'] == 'a clear thought'
    with pytest.raises(ContentError) as exc:
        parse_isolated('private-worker-source', wall_seconds=0.001)
    assert exc.value.code == 'CONTENT_COMPLEXITY_LIMIT'
    assert 'private-worker-source' not in str(exc.value)


def test_media_between_text_stays_schema_valid_and_video_is_manifest_only():
    doc = parse(f'before ![x](stmts-media:{ASSET_ID}) after', attachment_manifest=[ASSET_ID], attachment_resolver=lambda _: READY)
    assert [node['type'] for node in doc['blocks']] == ['paragraph', 'media', 'paragraph']
    Draft202012Validator(SCHEMA).validate(doc)
    video = replace(READY, kind='video')
    doc = parse('text', attachment_manifest=[ASSET_ID], attachment_resolver=lambda _: video)
    assert not doc['validationErrors']
    assert [node['type'] for node in doc['blocks']] == ['paragraph']


def test_distinct_manifest_assets_enforce_media_limit_and_mixing():
    ids = [f'11111111-1111-4111-8111-{number:012d}' for number in range(5)]
    with pytest.raises(ContentError): parse('text', attachment_manifest=ids)
    doc = parse('text', attachment_manifest=ids[:2], attachment_resolver=lambda x: replace(READY, attachment_id=x, kind='video' if x == ids[0] else 'image'))
    assert any('not both' in error for error in doc['validationErrors'])


def test_default_total_node_budget_on_punctuation_heavy_source():
    with pytest.raises(ContentError) as exc: parse('*a* ' * 8000)
    assert exc.value.code == 'CONTENT_COMPLEXITY_LIMIT'



def test_invalid_manifest_never_reaches_resolver():
    calls = []
    with pytest.raises(ContentError):
        parse('text', attachment_manifest=['https://foreign.test/object'], attachment_resolver=lambda x: calls.append(x))
    assert calls == []


@pytest.mark.parametrize('paragraphs,accepted', [(1, True), (2, True), (3, False)])
def test_table_heavy_exact_block_boundary(paragraphs, accepted):
    # Six table/header/section blocks plus 664 rows × three nodes = 1,998.
    source = '| A | B |\n| --- | --- |\n' + '| 1 | 2 |\n' * 664 + '\n' + '\n\n'.join(['word'] * paragraphs)
    if accepted:
        assert parse(source)
    else:
        with pytest.raises(ContentError) as exc: parse(source)
        assert exc.value.code == 'CONTENT_BLOCK_LIMIT'


def test_injected_node_allocator_and_unique_id_guard():
    allocator = iter(['paragraph-id', 'text-id'])
    doc = parse('word', id_allocator=lambda: next(allocator))
    assert [node['id'] for node in walk(doc['blocks'])] == ['paragraph-id', 'text-id']
    with pytest.raises(ContentError): parse('word', id_allocator=lambda: 'duplicate')


def test_structured_failure_matches_openapi_error_contract():
    import yaml
    from content.http import content_error_response
    api = yaml.safe_load((ROOT / 'contracts/openapi.yaml').read_text())
    error = ContentError('Nesting exceeds 12 block levels', 'CONTENT_DEPTH_LIMIT', [0, 1])
    response = content_error_response(error, 'request-1')
    Draft202012Validator({'$ref': '#/components/schemas/Error', 'components': api['components']}).validate(response.data)


def test_promoted_media_and_split_paragraphs_have_precise_line_spans():
    source = f'before\n![x](stmts-media:{ASSET_ID})\nafter'
    doc = parse(source, attachment_manifest=[ASSET_ID], attachment_resolver=lambda _: READY)
    assert [node['sourceSpan'] for node in doc['blocks']] == [[0, 1], [1, 2], [2, 3]]
    Draft202012Validator(SCHEMA).validate(doc)
