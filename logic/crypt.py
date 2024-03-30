from cryptography.fernet import Fernet


def encrypt_string(key, string_to_encrypt):
    f = Fernet(key)
    encrypted_string = f.encrypt(string_to_encrypt.encode())
    return encrypted_string


def decrypt_string(key, encrypted_string):
    f = Fernet(key)
    decrypted_string = f.decrypt(encrypted_string).decode()
    return decrypted_string


def generate_key():
    return Fernet.generate_key().decode()
