import urllib.request, json
API='http://127.0.0.1:5000/api/emprestimos'
req = urllib.request.Request(API, data=json.dumps({'id_livro':1,'id_usuario':5}).encode('utf-8'), headers={'Content-Type':'application/json'})
try:
    with urllib.request.urlopen(req) as r:
        print(r.getcode())
        print(r.read().decode())
except urllib.error.HTTPError as e:
    print('HTTPERR', e.code, e.read().decode())
except Exception as e:
    print('ERR', e)
