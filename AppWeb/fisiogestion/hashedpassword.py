import base64
import hashlib
import secrets
import getpass
import re

def make_django_password(password, salt=None, iterations=260000):
    """
    Genera un hash de contraseña en formato Django usando PBKDF2-SHA256
    
    Args:
        password (str): Contraseña en texto plano
        salt (str, opcional): Valor salt. Si es None, se genera aleatoriamente
        iterations (int): Número de iteraciones (Django usa 260000 por defecto)
        
    Returns:
        str: Hash en formato Django: 'pbkdf2_sha256$iterations$salt$hash'
    """
    # Generar salt aleatorio compatible con Django (22 caracteres Base64)
    if salt is None:
        salt = secrets.token_urlsafe(16)[:22]  # 16 bytes -> 22 caracteres Base64
        
    # Codificar la contraseña y el salt
    password_bytes = password.encode('utf-8')
    salt_bytes = salt.encode('utf-8')
    
    # Generar hash PBKDF2
    dk = hashlib.pbkdf2_hmac(
        'sha256',
        password_bytes,
        salt_bytes,
        iterations
    )
    
    # Codificar el hash en Base64 compatible con Django
    hash_b64 = base64.b64encode(dk).decode('ascii')
    hash_b64 = re.sub(r'[\+\/=]', lambda m: {'+': '.', '/': '_', '=': ''}[m.group()], hash_b64)
    
    # Formato Django: algoritmo$iteraciones$salt$hash
    return f"pbkdf2_sha256${iterations}${salt}${hash_b64}"

if __name__ == "__main__":
    # Pedir contraseña de forma segura
    password = getpass.getpass("Ingresa la contraseña para el usuario de Django: ")
    confirm = getpass.getpass("Confirma la contraseña: ")
    
    if password != confirm:
        print("\nError: Las contraseñas no coinciden")
        exit(1)
    
    # Generar hash en formato Django
    django_hash = make_django_password(password)
    
    print("\nHash de contraseña para Django:")
    print(django_hash)
    
    # Verificar formato (opcional)
    if django_hash.startswith("pbkdf2_sha256$") and django_hash.count("$") == 3:
        print("\n✅ Formato válido de Django")
    else:
        print("\n❌ Formato inválido")