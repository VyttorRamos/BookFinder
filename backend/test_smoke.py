import urllib.request
import json

def fetch(url):
    try:
        with urllib.request.urlopen(url, timeout=5) as r:
            status = r.getcode()
            body = r.read().decode('utf-8')
            print(f"URL: {url}\nSTATUS: {status}\nBODY:\n{body}\n")
    except Exception as e:
        print(f"URL: {url}\nERROR: {e}\n")

if __name__ == '__main__':
    print('Running smoke tests...')
    fetch('http://127.0.0.1:5000/api/listar-livros')
    fetch('http://127.0.0.1:5000/api/buscar-livros?q=python')
    fetch('http://localhost:5174/')
    fetch('http://127.0.0.1:5174/')
    # Try IPv6 localhost which Vite may bind to
    fetch('http://[::1]:5173/')
    fetch('http://[::1]:5174/')
