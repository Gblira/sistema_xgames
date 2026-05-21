import os
from fpdf import FPDF
from db import PDF_DIR, TIPOS_DOCUMENTO_REV

def _pdf_txt(texto):
    """Arial core font suporta latin-1; normaliza textos para impressao."""
    if texto is None:
        return ""
    texto = str(texto)
    mapa = {
        "—": "-",
        "–": "-",
        "’": "'",
        "“": '"',
        "”": '"',
    }
    for antigo, novo in mapa.items():
        texto = texto.replace(antigo, novo)
    return texto.encode("latin-1", "replace").decode("latin-1")

def _titulo_documento(tipo):
    if tipo == "ORCAMENTO":
        return "ORCAMENTO"
    return "ORDEM DE SERVICO"

def gerar_pdf_xgames(dados, modo_impressao="duas_vias"):
    """
    modo_impressao:
      - duas_vias: loja + cliente na mesma folha
      - via_loja: apenas via da loja
      - via_cliente: apenas via do cliente
    """
    os.makedirs(PDF_DIR, exist_ok=True)

    tipo = dados.get("tipo_documento", "OS")
    titulo_doc = _titulo_documento(tipo)
    tipo_label = _pdf_txt(TIPOS_DOCUMENTO_REV.get(tipo, "Ordem de Servico"))

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    
    # Desativa a quebra automatica para forçar tudo em 1 pagina
    pdf.set_auto_page_break(auto=False)

    def desenhar_via(y_offset, titulo_via):
        # --- CABEÇALHO ---
        pdf.set_xy(10, y_offset)
        pdf.set_fill_color(26, 26, 46)
        pdf.set_text_color(0, 212, 255)
        pdf.set_font("Arial", "B", 15)
        pdf.cell(190, 10, txt="X GAMES - ASSISTENCIA TECNICA", ln=True, align="C", fill=True)
        
        pdf.set_xy(10, y_offset + 10)
        pdf.set_text_color(255, 107, 0)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(190, 7, txt=titulo_doc, ln=True, align="C")
        
        pdf.set_xy(10, y_offset + 17)
        pdf.set_text_color(80, 80, 80)
        pdf.set_font("Arial", "I", 9)
        pdf.cell(190, 5, txt=_pdf_txt(f"({titulo_via}) - {tipo_label}"), ln=True, align="C")

        # --- DADOS ---
        pdf.set_text_color(0, 0, 0)
        pdf.set_xy(10, y_offset + 25)
        pdf.set_font("Arial", "B", 10)
        pdf.cell(95, 8, txt=_pdf_txt(f"N PEDIDO: {dados.get('n_pedido', '')}"), border=1)
        pdf.cell(95, 8, txt=_pdf_txt(f"DATA: {dados.get('data_registro', '')}"), border=1, ln=True)

        pdf.set_xy(10, y_offset + 33)
        pdf.cell(130, 8, txt=_pdf_txt(f"CLIENTE: {dados.get('nome_cliente', '')}"), border=1)
        pdf.cell(60, 8, txt=_pdf_txt(f"TEL: {dados.get('telefone', '')}"), border=1, ln=True)

        pdf.set_xy(10, y_offset + 41)
        end_txt = f"ENDERECO: {dados.get('endereco', '')} - {dados.get('bairro', '')} - CEP: {dados.get('cep', '')}"
        pdf.cell(190, 8, txt=_pdf_txt(end_txt[:95]), border=1, ln=True)

        pdf.set_xy(10, y_offset + 49)
        pdf.cell(65, 8, txt=_pdf_txt(f"APARELHO: {dados.get('aparelho', '')}"), border=1)
        pdf.cell(65, 8, txt=_pdf_txt(f"MODELO: {dados.get('modelo', '')}"), border=1)
        pdf.cell(60, 8, txt=_pdf_txt(f"SERIAL: {dados.get('serial', '')}"), border=1, ln=True)

        # --- CAIXA DE DESCRIÇÃO (Tamanho Fixo) ---
        pdf.set_xy(10, y_offset + 57)
        pdf.cell(190, 8, txt="DESCRICAO / RELATO:", border="LR T", ln=True)
        pdf.set_xy(10, y_offset + 65)
        pdf.set_font("Arial", size=10)
        
        # Remove quebras de linha extremas e limita o texto para nao vazar da caixa
        desc_text = str(dados.get("descricao", "") or "-").replace('\n', ' ')
        pdf.multi_cell(190, 5, txt=_pdf_txt(desc_text[:280])) 
        
        # Desenha o quadrado em volta da descricao garantindo que nada flutue
        pdf.rect(10, y_offset + 57, 190, 28)

        # --- VALORES E STATUS (Posição Absoluta) ---
        pdf.set_xy(10, y_offset + 85)
        pdf.set_font("Arial", "B", 10)
        try:
            valor = float(dados.get("valor_orcamento", 0) or 0)
        except ValueError:
            valor = 0.0
            
        pdf.cell(65, 8, txt=_pdf_txt(f"VALOR: R$ {valor:.2f}"), border=1)
        pdf.cell(65, 8, txt=_pdf_txt(f"PAGAMENTO: {dados.get('pagamento', '')}"), border=1)
        pdf.cell(60, 8, txt=_pdf_txt(f"SITUACAO: {dados.get('situacao', '')}"), border=1, ln=True)

        # --- RODAPÉ E ASSINATURA ---
        pdf.set_xy(10, y_offset + 95)
        pdf.set_font("Arial", "", 9)
        if tipo == "ORCAMENTO":
            rodape = (
                "Este documento e um ORCAMENTO. Valores e prazos podem variar apos "
                "analise tecnica. Validade: 7 dias. X GAMES."
            )
        else:
            rodape = (
                "Prezado(a) cliente, o conserto conta com 90 dias de garantia. "
                "Atenciosamente, X GAMES."
            )
        pdf.multi_cell(190, 4, txt=_pdf_txt(rodape), align="C")
        
        pdf.set_xy(10, y_offset + 105)
        pdf.cell(
            190,
            5,
            txt="ASSINATURA: ________________________________________________",
            ln=True,
            align="C",
        )

    # Lógica de posicionamento perfeito na Folha A4
    if modo_impressao == "duas_vias":
        desenhar_via(15, "VIA DA LOJA")
        
        # Desenha uma linha pontilhada no meio para auxiliar o corte
        pdf.set_draw_color(180, 180, 180)
        pdf.line(10, 135, 200, 135)
        pdf.set_draw_color(0, 0, 0)
        
        desenhar_via(145, "VIA DO CLIENTE")
    elif modo_impressao == "via_loja":
        desenhar_via(15, "VIA DA LOJA")
    else:
        desenhar_via(15, "VIA DO CLIENTE")

    prefixo = "OS" if tipo == "OS" else "ORC"
    nome_arquivo = f"{prefixo}_XGAMES_{dados.get('n_pedido', '0')}.pdf"
    caminho = os.path.join(PDF_DIR, nome_arquivo)
    pdf.output(caminho)
    return caminho