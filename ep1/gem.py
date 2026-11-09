import base64,json,subprocess,sys
img=sys.argv[1]; q=sys.argv[2]
a=base64.b64encode(open(img,'rb').read()).decode()
b={"model":"gemini-3.1-flash-lite","max_tokens":1200,"messages":[{"role":"user","content":[{"type":"text","text":q},{"type":"image_url","image_url":{"url":"data:image/jpeg;base64,"+a}}]}]}
open('/tmp/g.json','w').write(json.dumps(b))
r=subprocess.run(['curl','-s','-m','100','https://generativelanguage.googleapis.com/v1beta/openai/chat/completions','-H','Authorization: Bearer proxy-injected','-H','content-type: application/json','-d','@/tmp/g.json'],capture_output=True,text=True).stdout
try: print(json.loads(r)['choices'][0]['message']['content'])
except Exception: print(r[:500])
