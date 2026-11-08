"""Optional isolated parsing boundary for future request/worker adapters.

No HTTP endpoint is added. Attachment-aware services must install their own trusted
resolver inside the worker; caller-controlled media metadata is never accepted here.
"""
from dataclasses import asdict
import json
import os
from pathlib import Path
import subprocess
import sys

from .errors import ContentError
from .parser import Limits


def parse_isolated(source, *, title='', limits=None, memory_mb=256, wall_seconds=5.0):
    if memory_mb < 64 or wall_seconds <= 0:
        raise ValueError('Configure at least 64 MiB and a positive worker deadline')
    payload = {'source': source, 'title': title, 'limits': asdict(limits or Limits()), 'memoryMb': memory_mb}
    env = dict(os.environ)
    env['PYTHONPATH'] = str(Path(__file__).resolve().parents[1])
    try:
        result = subprocess.run([sys.executable, '-m', 'content.worker'], input=json.dumps(payload),
                                text=True, capture_output=True, timeout=wall_seconds, env=env)
    except subprocess.TimeoutExpired:
        raise ContentError('Content worker time limit exceeded', 'CONTENT_COMPLEXITY_LIMIT') from None
    if result.returncode:
        raise ContentError('Content worker resource limit exceeded', 'CONTENT_COMPLEXITY_LIMIT')
    try:
        outcome = json.loads(result.stdout)
    except (ValueError, TypeError):
        raise ContentError('Content worker did not return a valid result', 'CONTENT_COMPLEXITY_LIMIT') from None
    if 'error' in outcome:
        error = outcome['error']
        raise ContentError(error['message'], error['code'], error.get('sourceSpan'))
    return outcome['content']


def main():
    payload = json.load(sys.stdin)
    try:
        import resource
        cap = payload['memoryMb'] * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (cap, cap))
        from .parser import parse
        content = parse(payload['source'], title=payload['title'], limits=Limits(**payload['limits']))
        print(json.dumps({'content': content}))
    except ContentError as error:
        print(json.dumps({'error': {'code': error.code, 'message': str(error), 'sourceSpan': error.source_span}}))
    except (MemoryError, ImportError, OSError):
        # No source or stack trace is returned to callers.
        print(json.dumps({'error': {'code': 'CONTENT_COMPLEXITY_LIMIT', 'message': 'Content worker resource limit exceeded'}}))


if __name__ == '__main__':
    main()
