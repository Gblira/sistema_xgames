from db import DB_PATH, migrar_banco


def criar_banco():
    migrar_banco()
    print(f"Banco de dados configurado em: {DB_PATH}")


if __name__ == "__main__":
    criar_banco()
