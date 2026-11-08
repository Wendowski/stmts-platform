import os,sys,subprocess,time,urllib.request
from pathlib import Path
root=Path(__file__).resolve().parents[1]
processes=[]
try:
 api=subprocess.Popen([sys.executable,'backend/serve_fixture.py'],cwd=root,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);processes.append(api)
 for _ in range(30):
  try:
   urllib.request.urlopen('http://127.0.0.1:8000/v1/posts/11111111-1111-4111-8111-111111111111');break
  except Exception:time.sleep(.25)
 env=dict(os.environ,PORT='4000')
 web=subprocess.Popen(['node','web/dist/web/server/server.mjs'],cwd=root,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);processes.append(web)
 for _ in range(30):
  try:
   with urllib.request.urlopen('http://127.0.0.1:4000/') as response: html=response.read().decode()
   break
  except Exception:time.sleep(.25)
 else:raise RuntimeError('SSR server did not respond')
 assert 'A little more room to think.' in html
 assert 'Development preview' in html
 with urllib.request.urlopen('http://127.0.0.1:4000/?reader=1') as response: reader=response.read().decode()
 assert 'A quieter kind of conversation' in reader
 print('PASS: production SSR card and reader include API-backed fixture text in response HTML')
except Exception as e:
 print('FAIL:',repr(e));raise
finally:
 for p in processes:p.terminate()
