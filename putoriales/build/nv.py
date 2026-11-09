import json,urllib.request,time
def nv(prompt,model="minimaxai/minimax-m3.1-flash",max_tokens=3000,retries=2):
    body=json.dumps({"model":model,"messages":[{"role":"user","content":prompt}],"max_tokens":max_tokens}).encode()
    for i in range(retries+1):
        try:
            req=urllib.request.Request("https://integrate.api.nvidia.com/v1/chat/completions",data=body,headers={"Authorization":"Bearer proxy-injected","content-type":"application/json"})
            return json.load(urllib.request.urlopen(req,timeout=180))["choices"][0]["message"]["content"]
        except Exception as e: err=e;time.sleep(20)
    raise err
