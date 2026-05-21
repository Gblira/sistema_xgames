import os
import shutil
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _resolver_data_dir():
    """Funciona na pasta src/ (dev) e no executavel (data ao lado do app)."""
    candidatos = [
        os.path.join(BASE_DIR, "data"),
        os.path.join(BASE_DIR, "..", "data"),
    ]
    for caminho in candidatos:
        if os.path.isdir(caminho):
            return os.path.abspath(caminho)
    return os.path.abspath(os.path.join(BASE_DIR, "data"))


DATA_DIR = _resolver_data_dir()
DB_PATH = os.path.join(DATA_DIR, "sistema_xgames.db")
BACKUP_DIR = os.path.join(DATA_DIR, "backups")
PDF_DIR = os.path.join(DATA_DIR, "pdfs")

SITUACOES = [
    "Na loja",
    "Em conserto",
    "Aguardando peça",
    "Pronto para retirada",
    "Entregue",
    "Cancelado",
]

TIPOS_DOCUMENTO = {
    "Ordem de Serviço": "OS",
    "Orçamento": "ORCAMENTO",
}

TIPOS_DOCUMENTO_REV = {v: k for k, v in TIPOS_DOCUMENTO.items()}


def garantir_pastas():
    for pasta in (DATA_DIR, BACKUP_DIR, PDF_DIR):
        os.makedirs(pasta, exist_ok=True)


def get_connection():
    garantir_pastas()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def migrar_banco():
    garantir_pastas()
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS ordens_servico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            n_pedido TEXT,
            tipo_documento TEXT DEFAULT 'OS',
            data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            nome_cliente TEXT NOT NULL,
            rg TEXT,
            cep TEXT,
            endereco TEXT,
            bairro TEXT,
            telefone TEXT,
            aparelho TEXT,
            modelo TEXT,
            serial TEXT,
            descricao TEXT,
            valor_orcamento REAL,
            situacao TEXT DEFAULT 'Na loja',
            pagamento TEXT,
            data_retirada TEXT
        )
    """
    )

    cursor.execute("PRAGMA table_info(ordens_servico)")
    colunas = {row[1] for row in cursor.fetchall()}
    if "tipo_documento" not in colunas:
        cursor.execute(
            "ALTER TABLE ordens_servico ADD COLUMN tipo_documento TEXT DEFAULT 'OS'"
        )

    conn.commit()
    conn.close()


def proximo_pedido():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT MAX(CAST(n_pedido AS INTEGER)) FROM ordens_servico"
        )
        resultado = cursor.fetchone()[0]
        conn.close()
        return (int(resultado) + 1) if resultado else 1
    except (sqlite3.Error, TypeError, ValueError):
        return 1


def pedido_existe(n_pedido, excluir_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    if excluir_id:
        cursor.execute(
            "SELECT id FROM ordens_servico WHERE n_pedido = ? AND id != ?",
            (str(n_pedido), excluir_id),
        )
    else:
        cursor.execute(
            "SELECT id FROM ordens_servico WHERE n_pedido = ?",
            (str(n_pedido),),
        )
    existe = cursor.fetchone() is not None
    conn.close()
    return existe


def inserir_registro(dados):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO ordens_servico (
            n_pedido, tipo_documento, nome_cliente, rg, cep, endereco, bairro,
            telefone, aparelho, modelo, serial, descricao,
            valor_orcamento, situacao, pagamento, data_retirada
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        dados,
    )
    novo_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return novo_id


def atualizar_registro(registro_id, dados):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE ordens_servico SET
            n_pedido = ?, tipo_documento = ?, nome_cliente = ?, rg = ?, cep = ?,
            endereco = ?, bairro = ?, telefone = ?, aparelho = ?, modelo = ?,
            serial = ?, descricao = ?, valor_orcamento = ?, situacao = ?,
            pagamento = ?, data_retirada = ?
        WHERE id = ?
    """,
        (*dados, registro_id),
    )
    conn.commit()
    conn.close()


def excluir_registro(registro_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ordens_servico WHERE id = ?", (registro_id,))
    conn.commit()
    conn.close()


def buscar_por_id(registro_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ordens_servico WHERE id = ?", (registro_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def buscar_por_n_pedido(n_pedido):
    """Retorna o registro mais recente com esse numero de pedido."""
    if not str(n_pedido).strip():
        return None
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT * FROM ordens_servico
        WHERE n_pedido = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (str(n_pedido).strip(),),
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def contar_registros():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM ordens_servico")
    total = cursor.fetchone()[0]
    conn.close()
    return total


def obter_pedidos_existentes():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT n_pedido FROM ordens_servico")
    pedidos = {str(r[0]) for r in cursor.fetchall() if r[0] is not None}
    conn.close()
    return pedidos


def inserir_registros_lote(registros):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.executemany(
        """
        INSERT INTO ordens_servico (
            n_pedido, tipo_documento, nome_cliente, rg, cep, endereco, bairro,
            telefone, aparelho, modelo, serial, descricao,
            valor_orcamento, situacao, pagamento, data_retirada
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        registros,
    )
    conn.commit()
    conn.close()


def listar_registros(filtro="", situacao_filtro="Todas", tipo_filtro="Todos"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ordens_servico ORDER BY id DESC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()

    if not rows:
        return []

    if filtro:
        termo = filtro.lower()
        rows = [
            r
            for r in rows
            if termo in str(r.get("nome_cliente", "")).lower()
            or termo in str(r.get("n_pedido", "")).lower()
            or termo in str(r.get("telefone", "")).lower()
            or termo in str(r.get("serial", "")).lower()
            or termo in str(r.get("aparelho", "")).lower()
            or termo in str(r.get("modelo", "")).lower()
        ]

    if situacao_filtro != "Todas":
        rows = [r for r in rows if r.get("situacao") == situacao_filtro]

    if tipo_filtro == "OS":
        rows = [r for r in rows if r.get("tipo_documento", "OS") == "OS"]
    elif tipo_filtro == "ORCAMENTO":
        rows = [
            r for r in rows if r.get("tipo_documento", "OS") == "ORCAMENTO"
        ]

    return rows


def fazer_backup():
    garantir_pastas()
    if not os.path.exists(DB_PATH):
        return None
    nome = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    destino = os.path.join(BACKUP_DIR, nome)
    shutil.copy2(DB_PATH, destino)
    return os.path.abspath(destino)
