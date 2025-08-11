
import re
from validate_docbr import CPF, CNPJ

cpf_validator = CPF()
cnpj_validator = CNPJ()

def validar_cpf(cpf):
    return cpf_validator.validate(cpf)

def validar_cnpj(cnpj):
    return cnpj_validator.validate(cnpj)

def validar_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None
