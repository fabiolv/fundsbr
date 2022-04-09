from enum import unique
from mongoengine import Document, StringField

class Fund(Document):
    CNPJ = StringField(unique=True)
    NOME = StringField()
    FUNDO_TIPO = StringField()
    FUNDO_CLASSE = StringField()
    STATUS = StringField()
    DATA_INICIO = StringField()
    TAXA_ADM = StringField()
    TAXA_PERFORMANCE = StringField()
    INVESTIDOR_QUALIFICADO = StringField()
    INVESTIDOR_PROFISSIONAL = StringField()
    ADMIN_CNPJ = StringField()
    ADMIN = StringField()
    GESTOR_CNPJ = StringField()
    GESTOR = StringField()

if __name__ == '__main__':
    pass