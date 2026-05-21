import os
from datetime import datetime

import pandas as pd
import streamlit as st

from db import (
    SITUACOES,
    TIPOS_DOCUMENTO,
    TIPOS_DOCUMENTO_REV,
    atualizar_registro,
    excluir_registro,
    fazer_backup,
    inserir_registro,
    listar_registros,
    migrar_banco,
    pedido_existe,
    proximo_pedido,
    buscar_por_id,
    buscar_por_n_pedido,
    contar_registros,
)
from reports import gerar_pdf_xgames
from saros_theme import aplicar_tema_saros, rodape_saros, secao
from utils import buscar_endereco_por_cep, formatar_data_registro, limpar_cep, registro_para_pdf

migrar_banco()

st.set_page_config(
    page_title="X GAMES — Saros Edition",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

aplicar_tema_saros()

CAMPOS_FORM = [
    "form_n_pedido",
    "form_tipo_doc",
    "form_nome",
    "form_rg",
    "form_cep",
    "form_end",
    "form_bairro",
    "form_tel",
    "form_ap",
    "form_mod",
    "form_ser",
    "form_valor",
    "form_status",
    "form_pag",
    "form_retirada",
    "form_desc",
    "form_modo_pdf",
]


def _k(campo, prefixo=""):
    return f"{prefixo}{campo}" if prefixo else campo


def limpar_formulario_completo():
    for chave in list(st.session_state.keys()):
        if chave.startswith("form_") and not chave.startswith("edit_"):
            del st.session_state[chave]
        elif chave in (
            "os_salva",
            "dados_para_pdf",
            "modo_pdf_salvo",
            "pdf_hist_registro",
            "pdf_hist_modo",
            "form_registro_carregado_id",
        ):
            del st.session_state[chave]
    st.session_state["form_limpo"] = True


def processar_buscas_pendentes(prefixo=""):
    chave_pedido = _k("pedido_busca_pendente", prefixo)
    if chave_pedido in st.session_state and st.session_state[chave_pedido]:
        numero = str(st.session_state.pop(chave_pedido)).strip()
        registro = buscar_por_n_pedido(numero)
        if registro:
            carregar_registro_no_formulario(
                registro, prefixo, atualizar_pedido=(prefixo == "edit_")
            )
            if not prefixo:
                st.session_state.form_registro_carregado_id = registro["id"]
            st.session_state[_k("pedido_busca_ok", prefixo)] = numero
        else:
            if not prefixo:
                st.session_state.form_registro_carregado_id = None
            st.session_state[_k("pedido_busca_erro", prefixo)] = numero

    chave_cep = _k("cep_busca_pendente", prefixo)
    if chave_cep in st.session_state and st.session_state[chave_cep]:
        cep_valor = str(st.session_state.pop(chave_cep)).strip()
        endereco_dados, erro = buscar_endereco_por_cep(cep_valor)
        if erro:
            st.session_state[_k("cep_busca_erro", prefixo)] = erro
        else:
            st.session_state[_k("form_end", prefixo)] = endereco_dados["endereco"]
            st.session_state[_k("form_bairro", prefixo)] = endereco_dados["bairro"]
            st.session_state[_k("cep_busca_ok", prefixo)] = (
                f"{endereco_dados.get('cidade', '')}/{endereco_dados.get('uf', '')}"
            )


def carregar_registro_no_formulario(registro, prefixo="edit_", atualizar_pedido=True):
    if atualizar_pedido:
        st.session_state[_k("form_n_pedido", prefixo)] = str(registro.get("n_pedido", ""))
    st.session_state[_k("form_tipo_doc", prefixo)] = TIPOS_DOCUMENTO_REV.get(
        registro.get("tipo_documento", "OS"), "Ordem de Serviço"
    )
    st.session_state[_k("form_nome", prefixo)] = registro.get("nome_cliente", "") or ""
    st.session_state[_k("form_rg", prefixo)] = registro.get("rg", "") or ""
    st.session_state[_k("form_cep", prefixo)] = registro.get("cep", "") or ""
    st.session_state[_k("form_end", prefixo)] = registro.get("endereco", "") or ""
    st.session_state[_k("form_bairro", prefixo)] = registro.get("bairro", "") or ""
    st.session_state[_k("form_tel", prefixo)] = registro.get("telefone", "") or ""
    st.session_state[_k("form_ap", prefixo)] = registro.get("aparelho", "") or ""
    st.session_state[_k("form_mod", prefixo)] = registro.get("modelo", "") or ""
    st.session_state[_k("form_ser", prefixo)] = registro.get("serial", "") or ""
    st.session_state[_k("form_valor", prefixo)] = float(registro.get("valor_orcamento") or 0)
    st.session_state[_k("form_status", prefixo)] = registro.get("situacao") or "Na loja"
    st.session_state[_k("form_pag", prefixo)] = registro.get("pagamento", "") or ""
    st.session_state[_k("form_retirada", prefixo)] = registro.get("data_retirada", "") or ""
    st.session_state[_k("form_desc", prefixo)] = registro.get("descricao", "") or ""
    st.session_state[_k("form_modo_pdf", prefixo)] = "Duas vias (loja + cliente)"


def init_form_defaults(prefixo=""):
    chave_pedido = _k("form_n_pedido", prefixo)
    chave_limpo = "form_limpo" if not prefixo else "edit_form_limpo"
    if st.session_state.get(chave_limpo) or chave_pedido not in st.session_state:
        st.session_state[chave_pedido] = str(proximo_pedido())
        st.session_state[_k("form_tipo_doc", prefixo)] = "Ordem de Serviço"
        st.session_state[_k("form_nome", prefixo)] = ""
        st.session_state[_k("form_rg", prefixo)] = ""
        st.session_state[_k("form_cep", prefixo)] = ""
        st.session_state[_k("form_end", prefixo)] = ""
        st.session_state[_k("form_bairro", prefixo)] = ""
        st.session_state[_k("form_tel", prefixo)] = ""
        st.session_state[_k("form_ap", prefixo)] = ""
        st.session_state[_k("form_mod", prefixo)] = ""
        st.session_state[_k("form_ser", prefixo)] = ""
        st.session_state[_k("form_valor", prefixo)] = 0.0
        st.session_state[_k("form_status", prefixo)] = "Na loja"
        st.session_state[_k("form_pag", prefixo)] = ""
        st.session_state[_k("form_retirada", prefixo)] = ""
        st.session_state[_k("form_desc", prefixo)] = ""
        st.session_state[_k("form_modo_pdf", prefixo)] = "Duas vias (loja + cliente)"
        st.session_state[chave_limpo] = False
        if not prefixo:
            st.session_state.os_salva = False


def modo_pdf_para_parametro(label):
    mapa = {
        "Duas vias (loja + cliente)": "duas_vias",
        "Apenas via da LOJA": "via_loja",
        "Apenas via do CLIENTE": "via_cliente",
    }
    return mapa.get(label, "duas_vias")

def renderizar_formulario(prefixo="", titulo=""):
    processar_buscas_pendentes(prefixo)

    ok_ped = st.session_state.pop(_k("pedido_busca_ok", prefixo), None)
    if ok_ped:
        st.success(f"Pedido #{ok_ped} carregado com sucesso!")
    err_ped = st.session_state.pop(_k("pedido_busca_erro", prefixo), None)
    if err_ped:
        st.warning(f"Pedido #{err_ped} nao encontrado no cadastro.")

    ok_cep = st.session_state.pop(_k("cep_busca_ok", prefixo), None)
    if ok_cep:
        st.success(f"Endereco encontrado — {ok_cep}")
    err_cep = st.session_state.pop(_k("cep_busca_erro", prefixo), None)
    if err_cep:
        st.error(err_cep)

    init_form_defaults(prefixo)

    if titulo:
        st.subheader(titulo)

    secao("◈ Protocolo de Missão")
    col_t1, col_t2, col_t3 = st.columns([1, 1, 1.2])
    with col_t1:
        c_ped, c_busca_ped = st.columns([3, 1])
        with c_ped:
            n_pedido = st.text_input(
                "Nº PEDIDO",
                key=_k("form_n_pedido", prefixo),
                help="Digite o numero e clique na lupa para carregar um pedido existente.",
            )
        with c_busca_ped:
            st.write("")
            if st.button("🔍", key=_k("btn_busca_pedido", prefixo), use_container_width=True):
                st.session_state[_k("pedido_busca_pendente", prefixo)] = n_pedido
                st.rerun()
    with col_t2:
        st.text_input(
            "DATA",
            value=datetime.now().strftime("%d/%m/%Y %H:%M"),
            disabled=True,
            key=_k("data_display", prefixo),
        )
    with col_t3:
        tipo_doc_label = st.radio(
            "TIPO DE DOCUMENTO",
            options=list(TIPOS_DOCUMENTO.keys()),
            horizontal=True,
            key=_k("form_tipo_doc", prefixo),
            help="Use Orçamento quando o cliente só quer um preço estimado, sem deixar o aparelho.",
        )

    secao("◈ Dados do Cliente")
    col1, col2 = st.columns(2)
    with col1:
        nome = st.text_input("NOME DO CLIENTE", key=_k("form_nome", prefixo))
        rg = st.text_input("RG", key=_k("form_rg", prefixo))
        c_cep, c_btn = st.columns([3, 1])
        with c_cep:
            cep = st.text_input("CEP", key=_k("form_cep", prefixo), placeholder="00000-000")
        with c_btn:
            st.write("")
            if st.button("📍 Buscar", key=_k("btn_cep", prefixo), use_container_width=True):
                st.session_state[_k("cep_busca_pendente", prefixo)] = cep
                st.rerun()
        endereco = st.text_input("ENDEREÇO", key=_k("form_end", prefixo))
        bairro = st.text_input("BAIRRO", key=_k("form_bairro", prefixo))
    with col2:
        secao("◈ Equipamento & Status")
        telefone = st.text_input("TELEFONE", key=_k("form_tel", prefixo))
        aparelho = st.text_input(
            "APARELHO", key=_k("form_ap", prefixo), placeholder="Ex: PlayStation 5"
        )
        modelo = st.text_input("MODELO", key=_k("form_mod", prefixo))
        serial = st.text_input("SERIAL / IMEI", key=_k("form_ser", prefixo))
        valor = st.number_input(
            "VALOR (R$)",
            min_value=0.0,
            format="%.2f",
            key=_k("form_valor", prefixo),
        )
        status = st.selectbox("SITUAÇÃO", options=SITUACOES, key=_k("form_status", prefixo))
        pagamento = st.text_input("FORMA DE PAGAMENTO", key=_k("form_pag", prefixo))
        
        # --- LÓGICA DE DATA COM MÁSCARA AUTOMÁTICA ---
        chave_data = _k("form_retirada", prefixo)
        
        def aplicar_mascara_data():
            import re
            valor_digitado = st.session_state.get(chave_data, "")
            # Extrai apenas os números do que foi digitado
            nums = re.sub(r"\D", "", valor_digitado)
            
            # Formata automaticamente se tiver 8 dígitos (ex: 25122026) ou 6 dígitos (ex: 251226)
            if len(nums) == 8:
                st.session_state[chave_data] = f"{nums[:2]}/{nums[2:4]}/{nums[4:]}"
            elif len(nums) == 6:
                st.session_state[chave_data] = f"{nums[:2]}/{nums[2:4]}/20{nums[4:]}"

        data_retirada = st.text_input(
            "DATA DE RETIRADA",
            key=chave_data,
            placeholder="Ex: 25122026",
            help="Digite apenas os números. Ao apertar Enter ou sair do campo, as barras aparecerão.",
            on_change=aplicar_mascara_data
        ).strip()

        # Validação visual caso a pessoa digite números faltando ou sobrando
        if data_retirada:
            import re
            if not re.match(r"^\d{2}/\d{2}/\d{4}$", data_retirada):
                st.error("⚠️ Digite 6 ou 8 números para a data (Ex: 25122026 ou 251226).")
        # ------------------------------------------------------------

    desc = st.text_area(
        "DESCRIÇÃO / RELATO DO CLIENTE",
        key=_k("form_desc", prefixo),
        height=120,
    )

    modo_pdf_label = st.selectbox(
        "🖨️ Modo de impressão do PDF",
        ["Duas vias (loja + cliente)", "Apenas via da LOJA", "Apenas via do CLIENTE"],
        key=_k("form_modo_pdf", prefixo),
        help="Duas vias: mesma folha sulfite com cópia loja + cliente (padrão atual).",
    )

    return {
        "n_pedido": n_pedido,
        "tipo_doc_label": tipo_doc_label,
        "nome": nome,
        "rg": rg,
        "cep": limpar_cep(cep),
        "endereco": endereco,
        "bairro": bairro,
        "telefone": telefone,
        "aparelho": aparelho,
        "modelo": modelo,
        "serial": serial,
        "valor": valor,
        "status": status,
        "pagamento": pagamento,
        "data_retirada": data_retirada,
        "desc": desc,
        "modo_pdf_label": modo_pdf_label,
    }


def exibir_botao_pdf(dados, modo_label, nome_botao="📥 BAIXAR PDF PARA IMPRESSÃO"):
    caminho = gerar_pdf_xgames(dados, modo_pdf_para_parametro(modo_label))
    with open(caminho, "rb") as arquivo:
        prefixo = "OS" if dados.get("tipo_documento") == "OS" else "ORC"
        st.download_button(
            nome_botao,
            arquivo,
            file_name=os.path.basename(caminho),
            use_container_width=True,
            type="primary",
            key=f"dl_{dados.get('n_pedido')}_{modo_label}",
        )


# --- SIDEBAR: resumo rápido ---
with st.sidebar:
    st.markdown(
        '<div class="saros-sidebar-brand">SOLTARI · ECHELON IV</div>',
        unsafe_allow_html=True,
    )
    st.markdown("### ⚡ Painel Tático")
    todos = listar_registros()
    os_abertas = [r for r in todos if r.get("situacao") not in ("Entregue", "Cancelado")]
    prontas = [r for r in todos if r.get("situacao") == "Pronto para retirada"]
    orcamentos = [r for r in todos if r.get("tipo_documento") == "ORCAMENTO"]

    c1, c2 = st.columns(2)
    c1.metric("Em andamento", len(os_abertas))
    c2.metric("Prontas", len(prontas))
    st.metric("Orçamentos", len(orcamentos))
    st.metric("Total cadastrado", contar_registros())
    st.markdown("---")
    if st.button("💾 Fazer backup do banco", use_container_width=True):
        destino = fazer_backup()
        if destino:
            st.success(
                f"Backup salvo!\n\n"
                f"**Arquivo:** `{os.path.basename(destino)}`\n\n"
                f"**Pasta:**\n`{os.path.dirname(destino)}`"
            )
        else:
            st.error("Nenhum banco encontrado para backup.")

aba1, aba2, aba3 = st.tabs(
    ["⚡ Novo Cadastro", "◈ Editar Registro", "◎ Histórico & Impressão"]
)

# ===================== ABA 1: NOVO =====================
with aba1:
    if st.session_state.get("form_registro_carregado_id"):
        reg_vis = buscar_por_id(st.session_state.form_registro_carregado_id)
        if reg_vis:
            st.info(
                f"Pedido **#{reg_vis.get('n_pedido')}** carregado — "
                f"**{reg_vis.get('nome_cliente')}** | {reg_vis.get('aparelho', '')}. "
                "Visualize ou altere os dados. Ao salvar, o registro sera **atualizado**. "
                "Use **NOVO / LIMPAR** para um cadastro com numero novo."
            )

    dados_form = renderizar_formulario()

    c1, c2, _ = st.columns([1, 1, 2])
    with c1:
        if st.button("🚀 SALVAR REGISTRO", use_container_width=True, type="primary"):
            if not dados_form["nome"].strip() or not dados_form["aparelho"].strip():
                st.error("⚠️ Preencha pelo menos NOME e APARELHO.")
            else:
                registro_id = st.session_state.get("form_registro_carregado_id")
                if not registro_id and pedido_existe(dados_form["n_pedido"]):
                    existente = buscar_por_n_pedido(dados_form["n_pedido"])
                    registro_id = existente["id"] if existente else None

                if registro_id:
                    atualizar_registro(registro_id, montar_tupla_salvar(dados_form))
                    registro = buscar_por_id(registro_id)
                    st.session_state.form_registro_carregado_id = registro_id
                    msg = f"atualizado"
                else:
                    novo_id = inserir_registro(montar_tupla_salvar(dados_form))
                    registro = buscar_por_id(novo_id)
                    st.session_state.form_registro_carregado_id = novo_id
                    msg = "registrado"

                st.session_state.dados_para_pdf = registro_para_pdf(registro)
                st.session_state.modo_pdf_salvo = dados_form["modo_pdf_label"]
                st.session_state.os_salva = True
                tipo_txt = dados_form["tipo_doc_label"]
                st.success(f"✅ {tipo_txt} nº {dados_form['n_pedido']} {msg}!")
                st.rerun()

    with c2:
        if st.button("🔄 NOVO / LIMPAR", use_container_width=True):
            limpar_formulario_completo()
            st.rerun()

    if st.session_state.get("os_salva") and st.session_state.get("dados_para_pdf"):
        st.markdown("---")
        st.success("Documento salvo! Baixe o PDF abaixo para imprimir.")
        exibir_botao_pdf(
            st.session_state.dados_para_pdf,
            st.session_state.get("modo_pdf_salvo", "Duas vias (loja + cliente)"),
        )

# ===================== ABA 2: EDITAR =====================
with aba2:
    st.markdown("Carregue um registro pelo **ID** ou pela aba **Histórico** (botão Carregar).")

    col_id, col_load = st.columns([2, 1])
    with col_id:
        id_editar = st.number_input("ID do registro", min_value=0, step=1, key="edit_id_input")
    with col_load:
        st.write("")
        if st.button("🔎 Carregar para edição", use_container_width=True):
            reg = buscar_por_id(int(id_editar))
            if reg:
                st.session_state.edit_carregado_id = reg["id"]
                for chave in list(st.session_state.keys()):
                    if chave.startswith("edit_form_"):
                        del st.session_state[chave]
                carregar_registro_no_formulario(reg, prefixo="edit_", atualizar_pedido=True)
                st.session_state.edit_form_limpo = False
                st.success(f"Registro #{reg['id']} carregado.")
                st.rerun()
            else:
                st.error("ID não encontrado.")

    if st.session_state.get("edit_carregado_id"):
        st.info(f"Editando registro ID **{st.session_state.edit_carregado_id}**")
        dados_edit = renderizar_formulario(prefixo="edit_", titulo="Dados do registro")

        ec1, ec2 = st.columns(2)
        with ec1:
            if st.button("💾 SALVAR ALTERAÇÕES", use_container_width=True, type="primary"):
                rid = st.session_state.edit_carregado_id
                if not dados_edit["nome"].strip() or not dados_edit["aparelho"].strip():
                    st.error("⚠️ Preencha pelo menos NOME e APARELHO.")
                elif pedido_existe(dados_edit["n_pedido"], excluir_id=rid):
                    st.error("⚠️ Este número de pedido já está em uso por outro registro.")
                else:
                    atualizar_registro(rid, montar_tupla_salvar(dados_edit))
                    st.success("✅ Registro atualizado!")
                    st.rerun()
        with ec2:
            if st.button("🖨️ Gerar PDF deste registro", use_container_width=True):
                reg = buscar_por_id(st.session_state.edit_carregado_id)
                dados_pdf = registro_para_pdf(reg)
                exibir_botao_pdf(dados_pdf, dados_edit["modo_pdf_label"])

# ===================== ABA 3: HISTÓRICO =====================
with aba3:
    f1, f2, f3 = st.columns([2, 1, 1])
    with f1:
        busca = st.text_input(
            "🔎 Pesquisar",
            placeholder="Nome, pedido, telefone, serial, aparelho...",
        )
    with f2:
        filtro_sit = st.selectbox("Situação", ["Todas"] + SITUACOES)
    with f3:
        filtro_tipo = st.selectbox(
            "Tipo",
            ["Todos", "Ordem de Serviço (OS)", "Orçamento"],
        )

    tipo_map = {
        "Todos": "Todos",
        "Ordem de Serviço (OS)": "OS",
        "Orçamento": "ORCAMENTO",
    }
    registros = listar_registros(busca, filtro_sit, tipo_map[filtro_tipo])

    if registros:
        linhas = []
        for r in registros:
            tipo = r.get("tipo_documento", "OS")
            linhas.append(
                {
                    "ID": r["id"],
                    "Pedido": r.get("n_pedido"),
                    "Tipo": "OS" if tipo == "OS" else "Orçamento",
                    "Cliente": r.get("nome_cliente"),
                    "Aparelho": r.get("aparelho"),
                    "Situação": r.get("situacao"),
                    "Valor": f"R$ {float(r.get('valor_orcamento') or 0):.2f}",
                    "Data": formatar_data_registro(r.get("data_registro")),
                }
            )
        df = pd.DataFrame(linhas)
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("Ações no registro")

        opcoes_label = [
            f"#{r['id']} | Ped.{r.get('n_pedido')} | {r.get('nome_cliente')} | {r.get('aparelho')}"
            for r in registros
        ]
        mapa_sel = {lbl: r["id"] for lbl, r in zip(opcoes_label, registros)}

        sel_label = st.selectbox("Selecione o registro", opcoes_label)
        reg_id = mapa_sel[sel_label]
        reg_sel = buscar_por_id(reg_id)

        ac1, ac2, ac3, ac4 = st.columns(4)
        with ac1:
            if st.button("📂 Carregar p/ Editar", use_container_width=True):
                st.session_state.edit_carregado_id = reg_id
                for chave in list(st.session_state.keys()):
                    if chave.startswith("edit_form_"):
                        del st.session_state[chave]
                carregar_registro_no_formulario(reg_sel, prefixo="edit_", atualizar_pedido=True)
                st.session_state.edit_form_limpo = False
                st.success("Registro carregado! Vá na aba **Editar Registro**.")
                st.rerun()

        with ac2:
            modo_hist = st.selectbox(
                "Impressão",
                ["Duas vias (loja + cliente)", "Apenas via da LOJA", "Apenas via do CLIENTE"],
                key="hist_modo_pdf",
                label_visibility="collapsed",
            )

        with ac3:
            st.write("")
            if st.button("🖨️ Imprimir / PDF", use_container_width=True, type="primary"):
                st.session_state.pdf_hist_registro = registro_para_pdf(reg_sel)
                st.session_state.pdf_hist_modo = modo_hist

        with ac4:
            confirma = st.checkbox("Confirmo exclusão", key="conf_del")
            if st.button("🗑️ Excluir", use_container_width=True):
                if confirma:
                    excluir_registro(reg_id)
                    st.success("Registro excluído.")
                    st.rerun()
                else:
                    st.warning("Marque a confirmação antes de excluir.")

        if st.session_state.get("pdf_hist_registro"):
            st.markdown("---")
            exibir_botao_pdf(
                st.session_state.pdf_hist_registro,
                st.session_state.get("pdf_hist_modo", "Duas vias (loja + cliente)"),
                nome_botao="📥 BAIXAR PDF DO REGISTRO SELECIONADO",
            )
    else:
        st.info("Nenhum registro encontrado.")

rodape_saros()