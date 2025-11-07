# Arquivo: get_hash.py (Corrigido para usar a função SenhaHash)

# Importa a função REAL do seu código
from auth.auth_utils import SenhaHash 

senha_clara = "SenhaSegura123"
print(f"Hash Argon2 para '{senha_clara}':")
# Chama a função SenhaHash que você definiu
print(SenhaHash(senha_clara))