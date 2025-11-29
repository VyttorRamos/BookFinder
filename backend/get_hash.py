# Importa a função 
from auth.auth_utils import SenhaHash 

senha_clara = "SenhaSegura123"
print(f"Hash Argon2 para '{senha_clara}':")
# Chama a função SenhaHash 
print(SenhaHash(senha_clara))