import json
from pathlib import Path
import pytest
from jsonschema import validate
from content.parser import parse, safe_url, ContentError
ROOT=Path(__file__).resolve().parents[2]
def walk(nodes):
    for n in nodes:
        yield n
        yield from walk(n['children'])
@pytest.mark.parametrize('fixture',json.loads((ROOT/'design/reference/spec/markdown-fixtures.json').read_text()),ids=lambda x:x['id'])
def test_fixtures_are_safe_and_schema_valid(fixture):
    doc=parse(fixture['source'])
    validate(doc,json.loads((ROOT/'contracts/content.schema.json').read_text()))
    for n in walk(doc['blocks']):
        assert n['type']!='image'
        if 'url' in n:assert safe_url(n['url'])
    if fixture['id']=='raw-html':assert '<script>' in doc['plainText']
    if fixture['id']=='external-image':assert doc['validationErrors']
    if fixture['id']=='code':assert any(n['type']=='code' and '<script>' in n['text'] for n in walk(doc['blocks']))
    if fixture['id']=='basic':assert any(n['type']=='strong' for n in walk(doc['blocks']))
    if fixture['id']=='table':assert any(n['type']=='headerCell' for n in walk(doc['blocks']))
@pytest.mark.parametrize('url',['javascript:alert(1)','//evil.test','data:text/html,x','file:///tmp/x','https:\nevil.test'])
def test_unsafe_links(url):assert not safe_url(url)
def test_unicode_limit():
    assert parse('😀'*500)['isShort']
    with pytest.raises(ContentError):parse('😀'*50001)
def test_stable_block_identity():
    assert parse('First')['blocks'][0]['id']==parse('New paragraph\n\nFirst')['blocks'][1]['id']
def test_code_excluded_from_read_time():assert parse('```\n'+('word '*1000)+'\n```')['readingMinutes']==1
def test_read_only_api(client, settings):
    settings.DEBUG=True
    post=json.loads((ROOT/'contracts/fixtures/post.json').read_text())
    assert client.get('/v1/posts/'+post['id']).json()==post
    assert client.get('/v1/posts/00000000-0000-4000-8000-000000000000').status_code==404
    settings.DEBUG=False
    assert client.get('/v1/posts/'+post['id']).status_code==404
