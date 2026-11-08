"""Project the canonical JSON Schema into OpenAPI; there is only one node definition."""
import json
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]

def sync():
    schema = json.loads((ROOT / 'contracts/content.schema.json').read_text())
    names = {name: 'Block' if name == 'node' else 'Content' + name[0].upper() + name[1:] for name in schema['$defs']}
    def rewrite(value):
        if isinstance(value, list):
            return [rewrite(item) for item in value]
        if isinstance(value, dict):
            if '$ref' in value and value['$ref'].startswith('#/$defs/'):
                return {'$ref': '#/components/schemas/' + names[value['$ref'].split('/')[-1]]}
            return {key: rewrite(item) for key, item in value.items()}
        return value
    path = ROOT / 'contracts/openapi.yaml'
    api = yaml.safe_load(path.read_text())
    existing = api['components']['schemas']
    content = {key: value for key, value in schema.items() if key not in ('$schema', '$id', '$defs')}
    api['components']['schemas'] = {
        'Post': existing['Post'], 'Error': existing['Error'], 'Content': rewrite(content),
        **{names[name]: rewrite(definition) for name, definition in schema['$defs'].items()},
    }
    path.write_text(yaml.safe_dump(api, sort_keys=False, allow_unicode=True))

if __name__ == '__main__':
    sync()
