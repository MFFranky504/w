import json,sys,urllib.request,time
def gem(prompt,images=None,model="gemini-3.1-flash-lite",retries=2):
    content=[{"type":"text","text":prompt}]
    for im in images or []:
        content.append({"type":"image_url","image_url":{"url":"data:image/jpeg;base64,"+im}})
    body=json.dumps({"model":model,"messages":[{"role":"user","content":content if images else prompt}]}).encode()
    for i in range(retries+1):
        try:
            req=urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",data=body,headers={"Authorization":"Bearer proxy-injected","content-type":"application/json"})
            return json.load(urllib.request.urlopen(req,timeout=120))["choices"][0]["message"]["content"]
        except Exception as e:
            err=e;time.sleep(20)
    raise err
if __name__=="__main__":
    print(gem(sys.stdin.read()))
