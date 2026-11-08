"""Contract behavior independent of the Markdown implementation."""
from copy import deepcopy
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import pytest
import yaml

from content.parser import parse

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = json.loads((ROOT / 'contracts/content.schema.json').read_text())
VALIDATOR = Draft202012Validator(SCHEMA)
CASES = json.loads((ROOT / 'contracts/fixtures/canonical-cases.json').read_text())


def normalize(value):
    if isinstance(value, list):
        return [normalize(item) for item in value]
    if isinstance(value, dict):
        return {key: normalize(item) for key, item in value.items() if key not in ('id', 'sourceSpan')}
    return value


def test_schema_is_valid():
    Draft202012Validator.check_schema(SCHEMA)


@pytest.mark.parametrize('case', CASES, ids=lambda case: case['id'])
def test_shared_expected_canonical_documents_are_valid(case):
    VALIDATOR.validate(case['canonical'])


@pytest.mark.parametrize('case', CASES, ids=lambda case: case['id'])
def test_parser_matches_shared_expectations(case):
    actual = normalize(parse(case['source']))
    expected = normalize(case['canonical'])
    assert actual == expected


def container(kind, **extra):
    return {'id': 'block-1', 'type': kind, 'text': '', 'children': [], 'sourceSpan': [0, 1], **extra}


INVALID_NODES = [
    container('heading'),  # Heading depth is mandatory.
    container('heading', depth=7),
    container('heading', depth=0),
    container('paragraph', url='https://example.com'),
    container('paragraph', text='<b>hidden container payload</b>'),
    container('rule', children=[{'id': 'x', 'type': 'text', 'text': 'unexpected', 'children': []}]),
    container('list', children=[container('paragraph')]),
    container('table', children=[container('paragraph')]),
    container('row', children=[container('paragraph')]),
    container('code'),  # Language is explicit, including an empty string.
    {'id': 'link-1', 'type': 'link', 'text': '', 'children': []},
    {'id': 'link-1', 'type': 'link', 'text': '', 'children': [], 'url': 'javascript:alert(1)'},
    {'id': 'text-1', 'type': 'text', 'text': 'safe', 'children': [], 'html': '<script/>'},
    container('taskItem'),
    container('taskItem', checked='true'),
    container('media', attachmentId='not-a-uuid', mediaType='image', alt='A view', decorative=False, caption=''),
    container('media', attachmentId='11111111-1111-4111-8111-111111111111', mediaType='image', alt='a' * 1001, decorative=False, caption=''),
    container('media', attachmentId='11111111-1111-4111-8111-111111111111', mediaType='image', alt='A view', decorative=False, caption='', url='https://untrusted.test/x'),
]


@pytest.mark.parametrize('node', INVALID_NODES)
def test_variant_rejects_missing_or_unrelated_attributes(node):
    node_schema = {'$ref': '#/$defs/node', '$defs': SCHEMA['$defs']}
    assert list(Draft202012Validator(node_schema).iter_errors(node))


def test_inline_node_cannot_be_a_document_root():
    doc = deepcopy(CASES[0]['canonical'])
    doc['blocks'] = [{'id': 'x', 'type': 'text', 'text': 'text', 'children': []}]
    assert list(VALIDATOR.iter_errors(doc))


def test_openapi_reuses_exact_content_variants():
    api = yaml.safe_load((ROOT / 'contracts/openapi.yaml').read_text())
    names = {key: 'Block' if key == 'node' else 'Content' + key[0].upper() + key[1:] for key in SCHEMA['$defs']}
    def rewrite(value):
        if isinstance(value, list):
            return [rewrite(item) for item in value]
        if isinstance(value, dict):
            if '$ref' in value and value['$ref'].startswith('#/$defs/'):
                return {'$ref': '#/components/schemas/' + names[value['$ref'].split('/')[-1]]}
            return {key: rewrite(item) for key, item in value.items()}
        return value
    for key, variant in SCHEMA['$defs'].items():
        assert api['components']['schemas'][names[key]] == rewrite(variant)


def test_api_fixture_satisfies_openapi_response():
    api = yaml.safe_load((ROOT / 'contracts/openapi.yaml').read_text())
    schema = {'$ref': '#/components/schemas/Post', 'components': api['components']}
    post = json.loads((ROOT / 'contracts/fixtures/post.json').read_text())
    Draft202012Validator(schema).validate(post)


@pytest.mark.parametrize('node', [
    container('taskItem', checked=True),
    container('taskItem', checked=False),
    container('media', attachmentId='11111111-1111-4111-8111-111111111111', mediaType='image', alt='Green hills', decorative=False, caption=''),
])
def test_reserved_task_and_media_contract_variants(node):
    # Structural validity is not permission to publish or retrieve an attachment.
    node_schema = {'$ref': '#/$defs/node', '$defs': SCHEMA['$defs']}
    Draft202012Validator(node_schema).validate(node)


def test_shared_cases_cover_the_unchanged_designer_corpus():
    sources = json.loads((ROOT / 'design/reference/spec/markdown-fixtures.json').read_text())
    assert [(case['id'], case['source'], case['expect']) for case in CASES] == [
        (case['id'], case['source'], case['expect']) for case in sources
    ]


@pytest.mark.parametrize('case', CASES, ids=lambda case: case['id'])
def test_shared_fixture_logical_spans(case):
    def spans(nodes):
        result = []
        for node in nodes:
            if 'sourceSpan' in node:
                assert node['sourceSpan'][0] < node['sourceSpan'][1]
                result.append((node['type'], node['sourceSpan']))
            result.extend(spans(node['children']))
        return result
    assert spans(parse(case['source'])['blocks']) == spans(case['canonical']['blocks'])


def test_unknown_zero_span_placeholder_is_rejected():
    doc = deepcopy(CASES[0]['canonical'])
    doc['blocks'][0]['sourceSpan'] = [0, 0]
    assert list(VALIDATOR.iter_errors(doc))
