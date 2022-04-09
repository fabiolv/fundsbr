from mongoengine import Document, StringField

class Quote(Document):
    CNPJ = StringField()
    DATA = StringField()
    VALOR_QUOTA = StringField()
    VALOR_PATRIMONIAL = StringField()
    CAPTACAO_DIA = StringField()
    RESGATE_DIA = StringField()
    COTISTAS = StringField()

if __name__ == '__main__':
    pass