import re
from datetime import datetime
import requests

def formatar_data_registro(valor):
    # Se estiver vazio, não faz nada
    if not valor or str(valor).lower() == "nan":
        return ""
    
    # Converte de forma bruta para texto, limpa os espaços e corta as horas (se tiver)
    texto = str(valor).strip()
    texto_apenas_data = texto.split(' ')[0]
    
    # Retorna o valor original seguro, sem tentar colocar barras ou traços
    return texto_apenas_data


def limpar_cep(cep):
    return re.sub(r"\D", "", cep or "")


def buscar_endereco_por_cep(cep):
    cep_limpo = limpar_cep(cep)
    if len(cep_limpo) != 8:
        return None, "CEP deve ter 8 dígitos."

    try:
        resp = requests.get(
            f"https://viacep.com.br/ws/{cep_limpo}/json/",
            timeout=8,
        )
        resp.raise_for_status()
        dados = resp.json()
    except requests.RequestException:
        return None, "Sem conexão. Verifique a internet para buscar o CEP."

    if dados.get("erro"):
        return None, "CEP não encontrado."

    endereco = dados.get("logradouro", "")
    if dados.get("complemento"):
        endereco = f"{endereco}, {dados['complemento']}".strip(", ")

    return {
        "endereco": endereco,
        "bairro": dados.get("bairro", ""),
        "cidade": dados.get("localidade", ""),
        "uf": dados.get("uf", ""),
    }, None


def registro_para_pdf(registro):
    tipo = registro.get("tipo_documento", "OS")
    return {
        "n_pedido": registro.get("n_pedido", ""),
        "tipo_documento": tipo,
        "data_registro": formatar_data_registro(registro.get("data_registro")),
        "nome_cliente": registro.get("nome_cliente", ""),
        "telefone": registro.get("telefone", ""),
        "endereco": registro.get("endereco", ""),
        "bairro": registro.get("bairro", ""),
        "cep": registro.get("cep", ""),
        "aparelho": registro.get("aparelho", ""),
        "modelo": registro.get("modelo", ""),
        "serial": registro.get("serial", ""),
        "descricao": registro.get("descricao", ""),
        "valor_orcamento": registro.get("valor_orcamento", 0),
        "pagamento": registro.get("pagamento", ""),
        "situacao": registro.get("situacao", ""),
    }