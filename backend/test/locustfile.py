import json
from locust import HttpUser, task, between
from locust.exception import StopUser

# URL base da sua aplicação (local)
BASE_URL = "http://127.0.0.1:5000"

# --- Dados de Login VÁLIDOS ---
# AGORA CORRIGIDO: Chaves devem ser 'email' e 'senha' para corresponder ao app.py!
LOGIN_CREDENTIALS = {
    "email": "teste.carga@senai.br", # Chave de identidade
    "senha": "SenhaSegura123"      # Chave de senha (CORRIGIDA)
}

class AuthenticatedUser(HttpUser):
    # Simula o tempo de 'pensamento' do usuário
    wait_time = between(1, 5)
    host = BASE_URL 

    def on_start(self):
        self.login()

    def login(self):
        """Simula o login e captura o token JWT."""
        
        # Endpoint CORRETO: /auth/login (conforme app.py)
        LOGIN_ENDPOINT = "/auth/login" 
        
        # Envia a requisição com as chaves corrigidas (email e senha)
        response = self.client.post(LOGIN_ENDPOINT, json=LOGIN_CREDENTIALS, name=f"POST {LOGIN_ENDPOINT}")

        if response.status_code == 200:
            try:
                token = response.json().get("access_token") 
                self.client.headers = {"Authorization": f"Bearer {token}"}
                print(f"Login SUCESSO na URL: {LOGIN_ENDPOINT}")
            except json.JSONDecodeError:
                print("ERRO: Resposta de Login não é um JSON válido.")
                raise StopUser() 
        else:
            # Se falhar, imprime o erro para diagnóstico
            # O erro 400 agora deve estar resolvido. Se der 401, a senha do DB está errada.
            print(f"Login FALHOU com status: {response.status_code}. Resposta: {response.text}")
            raise StopUser()

    # --- CENÁRIOS DE TESTE PROTEGIDOS ---
    # Usaremos endpoints reais encontrados no app.py (rotas HTML/CRUD) para simular o tráfego.
    
    @task(3)
    def list_users(self):
        """Simula a listagem de usuários (ListarUsuarios)."""
        # Endpoint HTML (Simulando uma rota acessada após o login)
        self.client.get("/listaruser", name="GET /listaruser")

    @task(1)
    def list_books(self):
        """Simula a listagem de livros (ListarLivros)."""
        self.client.get("/listarlivro", name="GET /listarlivro")