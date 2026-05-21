import pyodbc
import sqlite3
import os

print("🚀 Iniciando a importação dos clientes...")

# 1. Localiza os arquivos automaticamente
arquivo_mdb = os.path.abspath("CADASTRO DE CLIENTES - X-GAMES.mdb")

caminhos_db = [
    os.path.abspath(os.path.join("src", "data", "sistema_xgames.db")),
    os.path.abspath(os.path.join("data", "sistema_xgames.db"))
]
caminho_sqlite = next((c for c in caminhos_db if os.path.exists(c)), None)

if not os.path.exists(arquivo_mdb):
    print("❌ Arquivo .mdb não encontrado! Coloque o 'CADASTRO DE CLIENTES - X-GAMES.mdb' nesta pasta.")
    exit()

if not caminho_sqlite:
    print("❌ Banco de dados do site não encontrado. Inicie o sistema pelo menos uma vez para criá-lo.")
    exit()

try:
    # 2. Conecta no site e zera a tabela
    conn_sqlite = sqlite3.connect(caminho_sqlite)
    cursor_sqlite = conn_sqlite.cursor()
    cursor_sqlite.execute("DELETE FROM ordens_servico")
    conn_sqlite.commit()
    print("✔️ Tabela do site zerada com sucesso.")

    # 3. Conecta no arquivo da loja
    conn_access = pyodbc.connect(rf"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={arquivo_mdb};")
    cursor_access = conn_access.cursor()
    
    # Descobre o nome da tabela (geralmente a primeira)
    tabelas = [t.table_name for t in cursor_access.tables(tableType='TABLE')]
    tabela_alvo = tabelas[0]

    # Lê as linhas
    cursor_access.execute(f"SELECT * FROM [{tabela_alvo}]")
    linhas = cursor_access.fetchall()
    print(f"✔️ {len(linhas)} clientes antigos encontrados no arquivo.")

    # 4. Prepara o formato para o site (Mapeando sua print)
    registros = []
    for linha in linhas:
        try:
            n_pedido = str(linha[0] or "")
            data_registro = str(linha[1] or "")  # A DATA QUE VOCÊ QUERIA!
            nome_cliente = str(linha[2] or "")
            rg = str(linha[3] or "")
            endereco = str(linha[4] or "")
            bairro = str(linha[5] or "")
            cep = str(linha[6] or "")
            telefone = str(linha[7] or "")
            aparelho = str(linha[8] or "")
            modelo = str(linha[9] or "")
            serial = str(linha[10] or "")
            descricao = str(linha[11] or "")
            
            # Limpa o dinheiro se vier como R$
            valor_orcamento = 0.0
            if linha[12]:
                v = str(linha[12]).replace("R$", "").replace(".", "").replace(",", ".").strip()
                try: valor_orcamento = float(v)
                except: pass

            situacao = str(linha[13] or "Na loja")
            pagamento = str(linha[14] or "")
            data_retirada = str(linha[15] or "")

            registros.append((
                n_pedido, "OS", data_registro, nome_cliente, rg, cep, endereco, 
                bairro, telefone, aparelho, modelo, serial, descricao, 
                valor_orcamento, situacao, pagamento, data_retirada
            ))
        except Exception as e:
            pass # Pula linhas com erro de formatação grave

    # 5. Injeta tudo no Site
    comando_sql = """
        INSERT INTO ordens_servico (
            n_pedido, tipo_documento, data_registro, nome_cliente, rg, cep, endereco, 
            bairro, telefone, aparelho, modelo, serial, descricao, 
            valor_orcamento, situacao, pagamento, data_retirada
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    cursor_sqlite.executemany(comando_sql, registros)
    conn_sqlite.commit()
    
    print("🎉 SUCESSO ABSOLUTO! Pode abrir o seu sistema.")

except Exception as e:
    print(f"❌ ERRO: {e}")
finally:
    try: conn_sqlite.close()
    except: pass
    try: conn_access.close()
    except: pass