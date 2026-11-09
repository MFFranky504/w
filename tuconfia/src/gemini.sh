#!/bin/bash
# Uso: gemini.sh "pregunta" [modelo]
# Llama a Gemini directo. La clave real la inyecta el proxy del entorno; "proxy-injected" es un valor falso.
# gemini-3.8-flash daba 502 y gemini-3.1-pro-preview se enfría seguido: el modelo por defecto es el que funciona.
M="${2:-gemini-3.1-flash-lite}"
python3 -c 'import json,sys;print(json.dumps({"model":sys.argv[1],"messages":[{"role":"user","content":sys.argv[2]}]}))' "$M" "$1" |
curl -s -m 120 https://generativelanguage.googleapis.com/v1beta/openai/chat/completions \
  -H "Authorization: Bearer proxy-injected" -H 'content-type: application/json' -d @- |
python3 -c 'import sys,json;d=json.load(sys.stdin);print(d["choices"][0]["message"]["content"] if "choices" in d else d)'
