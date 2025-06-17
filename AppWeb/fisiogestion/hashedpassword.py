import base64
import hashlib
import secrets
import getpass

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
    # Generar salt aleatorio si no se proporciona
    if salt is None:
        salt = secrets.token_hex(16)  # 16 bytes en hexadecimal
        
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
    
    # Codificar el hash en base64
    hash_b64 = base64.b64encode(dk).decode('ascii').strip()
    
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