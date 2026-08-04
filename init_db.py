from infrastructure.database.session import engine
from infrastructure.database.models import Base

def init_database():
    print("Criando tabelas no banco de dados...")
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso!")

if __name__ == "__main__":
    init_database()