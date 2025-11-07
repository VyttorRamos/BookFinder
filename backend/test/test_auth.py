# Arquivo: test_auth.py
from auth.auth_utils import hash_password, verify_password 
# ou o nome das suas funções de hash/verificação
import pytest
# Importa o módulo que contém as funções que queremos testar
from auth import hash_password, verify_password
from argon2.exceptions import VerifyMismatchError

# --- Cenário TU-001: Hashing de Senha Válida ---
def test_tu001_password_hashing_creates_valid_hash():
    """Verifica se o hash é gerado corretamente e não é o texto claro."""
    senha_exemplo = "senhaforte123"
    hashed = hash_password(senha_exemplo)

    # 1. Deve ser uma string diferente da senha original (Segurança)
    assert senha_exemplo != hashed
    # 2. O hash de Argon2 tem um formato específico e é longo
    assert hashed.startswith('$argon2id$')
    print(f"\n[TU-001 SUCESSO] Hash gerado: {hashed}")


# --- Cenário TU-002: Verificação de Senha Correta ---
def test_tu002_password_verification_success():
    """Verifica se a senha correta é validada com sucesso."""
    senha = "senhaforte123"
    hashed = hash_password(senha)
    
    # Deve retornar True para a senha correta
    assert verify_password(hashed, senha) is True
    print("\n[TU-002 SUCESSO] Verificação de senha correta.")


# --- Cenário TU-003: Verificação de Senha Incorreta (Tratamento de Erro) ---
def test_tu003_password_verification_failure():
    """Verifica se a senha incorreta é rejeitada (False)."""
    senha_correta = "senhaforte123"
    senha_incorreta = "senhaerrada456"
    hashed = hash_password(senha_correta)
    
    # Deve retornar False para a senha incorreta
    assert verify_password(hashed, senha_incorreta) is False
    print("\n[TU-003 SUCESSO] Verificação de senha incorreta rejeitada.")