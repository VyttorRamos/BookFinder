import urllib.request, urllib.parse, json, time

API_BASE = 'http://127.0.0.1:5000'

def post_json(path, payload):
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(API_BASE + path, data=data, headers={'Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.getcode(), json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ''
        return e.code, body
    except Exception as e:
        return None, str(e)

if __name__ == '__main__':
    print('API E2E: register -> login')
    ts = int(time.time())
    email = f'test_user_{ts}@example.com'
    senha = 'TestPass123'
    payload = {'nome_completo': 'Teste E2E', 'email': email, 'senha': senha, 'telefone': '00000000'}
    status, body = post_json('/auth/register', payload)
    print('REGISTER', status, body)
    status, body = post_json('/auth/login', {'email': email, 'senha': senha})
    print('LOGIN', status, body)
    if status == 200 and isinstance(body, dict) and body.get('access_token'):
        print('\nE2E auth OK - token received')
    else:
        print('\nE2E auth failed')
