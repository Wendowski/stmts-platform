"""Explicit development fixture generation; never called during production startup."""
import json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'backend'))
from content.parser import parse
path=root/'contracts/fixtures/post.json'
post=json.loads(path.read_text())
post['content']=parse((root/'contracts/fixtures/article.md').read_text())
text=json.dumps(post,ensure_ascii=False,indent=2)+'\n'
for dest in [path,root/'web/public/development-post.json',root/'ios/Sources/STMTSReader/Resources/post.json',root/'android/app/src/main/assets/post.json']:
 dest.write_text(text)
