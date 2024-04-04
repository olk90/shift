from cryptography.fernet import Fernet

from logic.config import properties
from logic.model import Employee


def encrypt_string(key, string_to_encrypt):
    f = Fernet(key)
    encrypted_string = f.encrypt(string_to_encrypt.encode()).decode()
    return encrypted_string


def decrypt_string(key, encrypted_string):
    f = Fernet(key)
    decrypted_string = f.decrypt(encrypted_string).decode()
    return decrypted_string


def generate_key():
    return Fernet.generate_key().decode()


def encrypt_employees(key):
    s = properties.open_session()
    employees = s.query(Employee).all()
    for employee in employees:
        encrypt_employee(key, employee)
    s.commit()
    s.close()


def encrypt_employee(key, employee: Employee) -> Employee:
    enc_fn = encrypt_string(key, employee.firstname)
    enc_ln = encrypt_string(key, employee.lastname)
    employee.firstname = enc_fn
    employee.lastname = enc_ln
    return employee


def decrypt_employees(key):
    s = properties.open_session()
    employees = s.query(Employee).all()
    for employee in employees:
        decrypt_employee(key, employee)
    s.commit()
    s.close()


def decrypt_employee(key, employee: Employee) -> Employee:
    enc_fn = decrypt_string(key, employee.firstname)
    enc_ln = decrypt_string(key, employee.lastname)
    employee.firstname = enc_fn
    employee.lastname = enc_ln
    return employee
