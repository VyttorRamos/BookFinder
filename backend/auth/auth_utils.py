from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError
from typing import Optional, Tuple

ph = PasswordHasher()

def SenhaHash(SenhaSimples: str) ->str:
    #recebe a senha em texto e retorna o hash Argon2 - string
    return ph.hash(SenhaSimples)

def VerificaSenha(HashArmazenada: str, SenhaSimples: str) ->  Tuple[bool, Optional[str]]:
    #Verifica se SenhaSimples corresponde ao HashArmazenado, retorna uma tupla(is_valid, new_hash_or_None).
    try:
        ph.verify(HashArmazenada, SenhaSimples)
        if ph.check_needs_rehash(HashArmazenada):
            NovaHash = ph.hash(SenhaSimples)
            return True, NovaHash
        return True, None
    except(VerifyMismatchError, VerificationError):
        return False, None
    
