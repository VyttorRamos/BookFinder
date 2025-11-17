import urllib.request, urllib.parse, json, time

API = 'http://127.0.0.1:5000'


def post(path, payload):
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(API + path, data=data, headers={'Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.getcode(), json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ''
        return e.code, body
    except Exception as e:
        return None, str(e)


def get(path):
    try:
        with urllib.request.urlopen(API + path, timeout=10) as r:
            return r.getcode(), json.loads(r.read().decode())
    except Exception as e:
        return None, str(e)


if __name__ == '__main__':
    report = []
    ts = int(time.time())
    email = f'e2e_user_{ts}@example.com'
    senha = 'E2EPass123'

    print('1) Register user')
    status, body = post('/auth/register', {'nome_completo':'E2E Tester','email':email,'senha':senha,'telefone':'000'})
    print(status, body)
    report.append(('register', status, body))

    print('\n2) Login user')
    status, body = post('/auth/login', {'email':email,'senha':senha})
    print(status, body)
    report.append(('login', status, body))

    if status != 200 or not isinstance(body, dict) or 'access_token' not in body:
        print('Login failed, aborting E2E')
        exit(1)

    token = body['access_token']
    refresh = body.get('refresh_token')

    # helper to call protected endpoints
    def call(method, path, payload=None):
        headers = {'Authorization': 'Bearer ' + token}
        if payload is not None:
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(API+path, data=data, headers={'Content-Type':'application/json', 'Authorization': headers['Authorization']}, method=method)
        else:
            req = urllib.request.Request(API+path, headers={'Authorization': headers['Authorization']}, method=method)
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                return r.getcode(), json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            body = e.read().decode() if e.fp else ''
            return e.code, body
        except Exception as e:
            return None, str(e)

    print('\n3) Create genre')
    status, body = call('POST', '/api/generos', {'nome_genero':'E2E Genre','descricao':'desc'})
    print(status, body)
    report.append(('create_genero', status, body))

    print('\n4) Create publisher')
    status, body = call('POST', '/api/editoras', {'nome':'E2E Publisher','endereco':'x','telefone':'x','email':'x@x'})
    print(status, body)
    report.append(('create_editora', status, body))

    print('\n5) Create book')
    # try to resolve created editora and genero ids
    id_editora = None
    id_genero = None
    try:
        sc, editoras = get('/api/editoras')
        if sc == 200 and isinstance(editoras, dict):
            for e in editoras.get('editoras', []):
                if e.get('nome') == 'E2E Publisher':
                    # editoras are returned with key 'id' mapped from 'id_editora'
                    id_editora = e.get('id') or e.get('id_editora')
                    break
        sc, generos = get('/api/generos')
        if sc == 200 and isinstance(generos, dict):
            for g in generos.get('generos', []):
                # genero row keys may be 'nome' and 'id_categoria'
                name = g.get('nome_genero') or g.get('nome')
                if name == 'E2E Genre':
                    # collect possible id keys
                    id_genero = g.get('id') or g.get('id_genero') or g.get('id_categoria')
                    break
        # debug prints
        print('Found editora id:', id_editora)
        print('Found genero id:', id_genero)
    except Exception:
        pass

    payload = {'titulo':'E2E Book','isbn': f'123456-{ts}', 'ano_publicacao':'2023'}
    if id_editora:
        payload['id_editora'] = id_editora
    if id_genero:
        payload['id_categoria'] = id_genero

    status, body = call('POST', '/api/livros', payload)
    print(status, body)
    report.append(('create_livro', status, body))

    print('\n6) List books')
    status, body = get('/api/listar-livros')
    print(status, type(body))
    report.append(('list_livros', status, body))

    # attempt create emprestimo (pick first book and first usuario)
    livros = body.get('livros') if isinstance(body, dict) else []
    if livros:
        livro_id = livros[0].get('id')
        print('\n7) List usuarios')
        status, body2 = get('/api/usuarios')
        print(status, body2)
        report.append(('list_usuarios', status, body2))
        usuarios = body2.get('usuarios') if isinstance(body2, dict) else []
        if usuarios:
            usuario_id = usuarios[0].get('id')
            # Create a copia via API so emprestimo can be created
            try:
                sc, b = call('POST', '/api/copias', {'id_livro': livro_id, 'cod_interno': f'E2E-{livro_id}-{ts}', 'status_copia': 'disponivel'})
                print('copias POST ->', sc, b)
            except Exception as e:
                print('Failed to create copia via API:', e)

            print('\n8) Create emprestimo')
            status, body = call('POST', '/api/emprestimos', {'id_livro': livro_id, 'id_usuario': usuario_id})
            print(status, body)
            report.append(('create_emprestimo', status, body))
        else:
            print('No usuarios found to test emprestimo')
    else:
        print('No livros available to test emprestimo')

    print('\nE2E report:')
    for r in report:
        print(r)
    
    print('\nDone')
