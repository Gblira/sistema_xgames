# 🎮 Sistema X-Games - Gestão de Assistência Técnica

Este é um sistema completo desenvolvido em Python para o gerenciamento de entrada, manutenção e saída de equipamentos em uma assistência técnica. Ele substitui planilhas e sistemas legados por uma interface web moderna, rápida e intuitiva.

## ✨ Funcionalidades Principais

* **Gestão de Ordens de Serviço (OS) e Orçamentos:** Cadastro completo de clientes, aparelhos, defeitos relatados e valores.
* **Controle de Status:** Acompanhamento em tempo real da situação de cada aparelho (Na loja, Em conserto, Aguardando peça, Pronto para retirada, Entregue, Cancelado).
* **Preenchimento Automático de Endereço:** Integração com a API do ViaCEP para buscar logradouro e bairro automaticamente a partir do CEP.
* **Geração de PDF:** Exportação automática das Ordens de Serviço prontas para impressão e entrega ao cliente.
* **Migração de Dados Legados:** Ferramenta integrada (via `pyodbc`) para importar e higienizar grandes volumes de clientes de bancos de dados antigos do Microsoft Access (`.mdb`) direto para o SQLite.
* **Busca e Histórico:** Filtros avançados para localizar rapidamente pedidos antigos por nome, serial do aparelho, telefone ou número do pedido.

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3
* **Interface Web:** Streamlit
* **Banco de Dados:** SQLite (Nativo) e manipulação de MS Access (`.mdb`) para migrações.
* **Bibliotecas em destaque:** * `requests` (Integração ViaCEP)
  * `fpdf2` (Geração de documentos PDF)
  * `pyodbc` (Leitura de dados legados)

## 🚀 Como executar o projeto localmente

1. Clone este repositório:
   ```bash
   git clone [https://github.com/Gblira/sistema-xgames.git](https://github.com/Gblira/sistema-xgames.git)