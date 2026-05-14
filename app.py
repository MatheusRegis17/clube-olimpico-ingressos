import streamlit as st
import pandas as pd
from datetime import datetime

# =========================================================
# CONFIGURAÇÃO PRINCIPAL
# =========================================================

st.set_page_config(
    page_title="Clube Olímpico Ingressos",
    page_icon="🎟️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# ESTILO VISUAL
# =========================================================

st.markdown(
    """
    <style>
        .main {
            background-color: #0e1117;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        .titulo-principal {
            font-size: 42px;
            font-weight: 800;
            color: #ffffff;
            margin-bottom: 0px;
        }

        .subtitulo {
            font-size: 18px;
            color: #b8c1ec;
            margin-top: 0px;
            margin-bottom: 25px;
        }

        .card {
            background: linear-gradient(135deg, #161b22, #1f2937);
            border: 1px solid #30363d;
            border-radius: 18px;
            padding: 22px;
            box-shadow: 0 6px 20px rgba(0,0,0,0.25);
            margin-bottom: 16px;
        }

        .card h3 {
            color: #ffffff;
            margin-bottom: 6px;
        }

        .card p {
            color: #c9d1d9;
            margin-bottom: 0;
        }

        .mesa-disponivel {
            background-color: #1f8f4d;
            color: white;
            padding: 10px;
            border-radius: 10px;
            text-align: center;
            font-weight: bold;
            margin: 3px;
        }

        .mesa-reservada {
            background-color: #d9a300;
            color: black;
            padding: 10px;
            border-radius: 10px;
            text-align: center;
            font-weight: bold;
            margin: 3px;
        }

        .mesa-vendida {
            background-color: #b42318;
            color: white;
            padding: 10px;
            border-radius: 10px;
            text-align: center;
            font-weight: bold;
            margin: 3px;
        }

        .rodape {
            color: #8b949e;
            font-size: 13px;
            margin-top: 30px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# DADOS TEMPORÁRIOS PARA TESTE
# Depois vamos trocar isso pelo Google Sheets.
# =========================================================

if "mesas" not in st.session_state:
    st.session_state.mesas = pd.DataFrame({
        "mesa": list(range(1, 101)),
        "status": ["Disponível"] * 100,
        "comprador": [""] * 100,
        "telefone": [""] * 100,
        "vendedor": [""] * 100,
        "pagamento": [""] * 100,
        "valor": [40.00] * 100,
        "data_hora": [""] * 100
    })

if "ingressos" not in st.session_state:
    st.session_state.ingressos = pd.DataFrame(columns=[
        "comprador",
        "telefone",
        "quantidade",
        "vendedor",
        "pagamento",
        "total",
        "data_hora"
    ])

# =========================================================
# FUNÇÕES
# =========================================================

def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def calcular_resumo():
    mesas = st.session_state.mesas
    ingressos = st.session_state.ingressos

    mesas_vendidas = len(mesas[mesas["status"] == "Vendida"])
    mesas_reservadas = len(mesas[mesas["status"] == "Reservada"])
    mesas_disponiveis = len(mesas[mesas["status"] == "Disponível"])

    receita_mesas = mesas_vendidas * 40.00
    receita_ingressos = ingressos["total"].sum() if not ingressos.empty else 0
    receita_total = receita_mesas + receita_ingressos

    return {
        "mesas_vendidas": mesas_vendidas,
        "mesas_reservadas": mesas_reservadas,
        "mesas_disponiveis": mesas_disponiveis,
        "receita_mesas": receita_mesas,
        "receita_ingressos": receita_ingressos,
        "receita_total": receita_total
    }


def exibir_mesa_card(numero, status):
    if status == "Disponível":
        classe = "mesa-disponivel"
    elif status == "Reservada":
        classe = "mesa-reservada"
    else:
        classe = "mesa-vendida"

    st.markdown(
        f"<div class='{classe}'>Mesa {numero}<br>{status}</div>",
        unsafe_allow_html=True
    )

# =========================================================
# MENU LATERAL
# =========================================================

st.sidebar.title("🎟️ Clube Olímpico")
st.sidebar.caption("Sistema de ingressos e eventos")

pagina = st.sidebar.radio(
    "Menu",
    [
        "Dashboard",
        "Mapa de Mesas",
        "Vender Mesa",
        "Ingressos Individuais",
        "Relatórios"
    ]
)

st.sidebar.divider()

evento_ativo = st.sidebar.selectbox(
    "Evento ativo",
    ["Festa Junina 2026"]
)

st.sidebar.info(
    """
    **Evento:** Festa Junina 2026  
    **Data:** 04/07/2026  
    **Local:** Quadra do Clube
    """
)

# =========================================================
# CABEÇALHO
# =========================================================

st.markdown("<h1 class='titulo-principal'>Clube Olímpico Ingressos</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitulo'>Sistema de controle de mesas, ingressos e eventos</p>", unsafe_allow_html=True)

# =========================================================
# PÁGINA: DASHBOARD
# =========================================================

if pagina == "Dashboard":
    resumo = calcular_resumo()

    st.subheader("📊 Visão geral do evento")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Mesas disponíveis", resumo["mesas_disponiveis"])

    with col2:
        st.metric("Mesas reservadas", resumo["mesas_reservadas"])

    with col3:
        st.metric("Mesas vendidas", resumo["mesas_vendidas"])

    col4, col5, col6 = st.columns(3)

    with col4:
        st.metric("Receita com mesas", formatar_moeda(resumo["receita_mesas"]))

    with col5:
        st.metric("Receita com ingressos", formatar_moeda(resumo["receita_ingressos"]))

    with col6:
        st.metric("Receita total", formatar_moeda(resumo["receita_total"]))

    st.markdown("---")

    st.markdown(
        """
        <div class="card">
            <h3>🎪 Evento ativo</h3>
            <p><strong>Festa Junina 2026</strong><br>
            Data: 04/07/2026<br>
            Local: Quadra do Clube<br>
            Mesa: R$ 40,00<br>
            Ingresso individual: R$ 10,00</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================================================
# PÁGINA: MAPA DE MESAS
# =========================================================

elif pagina == "Mapa de Mesas":
    st.subheader("🪑 Mapa de Mesas")

    st.caption("Verde = disponível | Amarelo = reservada | Vermelho = vendida")

    mesas = st.session_state.mesas

    for inicio in range(0, 100, 10):
        cols = st.columns(10)
        for i, col in enumerate(cols):
            idx = inicio + i
            if idx < len(mesas):
                with col:
                    mesa = mesas.iloc[idx]
                    exibir_mesa_card(mesa["mesa"], mesa["status"])

# =========================================================
# PÁGINA: VENDER MESA
# =========================================================

elif pagina == "Vender Mesa":
    st.subheader("🧾 Registrar venda ou reserva de mesa")

    mesas = st.session_state.mesas

    mesas_disponiveis = mesas[mesas["status"] == "Disponível"]["mesa"].tolist()
    mesas_reservadas = mesas[mesas["status"] == "Reservada"]["mesa"].tolist()
    mesas_todas = mesas["mesa"].tolist()

    with st.form("form_venda_mesa"):
        mesa_numero = st.selectbox("Número da mesa", mesas_todas)

        comprador = st.text_input("Nome do comprador")
        telefone = st.text_input("Telefone / WhatsApp")
        vendedor = st.text_input("Vendedor")
        status = st.selectbox("Status", ["Reservada", "Vendida", "Disponível", "Cancelada"])
        pagamento = st.selectbox("Forma de pagamento", ["PIX", "Dinheiro", "Cartão", "Pendente", "Outro"])

        observacao = st.text_area("Observação", placeholder="Ex: aguardando comprovante, pedido feito por WhatsApp etc.")

        enviar = st.form_submit_button("Salvar mesa")

    if enviar:
        idx = st.session_state.mesas.index[st.session_state.mesas["mesa"] == mesa_numero][0]

        st.session_state.mesas.loc[idx, "status"] = status
        st.session_state.mesas.loc[idx, "comprador"] = comprador
        st.session_state.mesas.loc[idx, "telefone"] = telefone
        st.session_state.mesas.loc[idx, "vendedor"] = vendedor
        st.session_state.mesas.loc[idx, "pagamento"] = pagamento
        st.session_state.mesas.loc[idx, "valor"] = 40.00
        st.session_state.mesas.loc[idx, "data_hora"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        st.success(f"Mesa {mesa_numero} atualizada com sucesso!")

    st.markdown("---")
    st.subheader("Consulta rápida")

    mesa_consulta = st.selectbox("Consultar mesa", mesas_todas, key="consulta_mesa")
    dados_mesa = st.session_state.mesas[st.session_state.mesas["mesa"] == mesa_consulta].iloc[0]

    st.write(dados_mesa)

# =========================================================
# PÁGINA: INGRESSOS INDIVIDUAIS
# =========================================================

elif pagina == "Ingressos Individuais":
    st.subheader("🎫 Registrar ingressos individuais")

    with st.form("form_ingresso"):
        comprador = st.text_input("Nome do comprador")
        telefone = st.text_input("Telefone / WhatsApp")
        quantidade = st.number_input("Quantidade de ingressos", min_value=1, step=1)
        vendedor = st.text_input("Vendedor")
        pagamento = st.selectbox("Forma de pagamento", ["PIX", "Dinheiro", "Cartão", "Pendente", "Outro"])

        total = quantidade * 10.00
        st.info(f"Total: {formatar_moeda(total)}")

        enviar = st.form_submit_button("Salvar venda de ingresso")

    if enviar:
        nova_linha = {
            "comprador": comprador,
            "telefone": telefone,
            "quantidade": quantidade,
            "vendedor": vendedor,
            "pagamento": pagamento,
            "total": total,
            "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }

        st.session_state.ingressos = pd.concat(
            [st.session_state.ingressos, pd.DataFrame([nova_linha])],
            ignore_index=True
        )

        st.success("Venda de ingresso registrada com sucesso!")

    st.markdown("---")
    st.subheader("Ingressos vendidos")

    st.dataframe(st.session_state.ingressos, use_container_width=True)

# =========================================================
# PÁGINA: RELATÓRIOS
# =========================================================

elif pagina == "Relatórios":
    st.subheader("📑 Relatórios")

    resumo = calcular_resumo()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total mesas", formatar_moeda(resumo["receita_mesas"]))

    with col2:
        st.metric("Total ingressos", formatar_moeda(resumo["receita_ingressos"]))

    with col3:
        st.metric("Total geral", formatar_moeda(resumo["receita_total"]))

    st.markdown("---")

    st.subheader("Mesas")
    st.dataframe(st.session_state.mesas, use_container_width=True)

    st.subheader("Ingressos")
    st.dataframe(st.session_state.ingressos, use_container_width=True)

    st.download_button(
        label="Baixar relatório de mesas em CSV",
        data=st.session_state.mesas.to_csv(index=False).encode("utf-8-sig"),
        file_name="relatorio_mesas.csv",
        mime="text/csv"
    )

    st.download_button(
        label="Baixar relatório de ingressos em CSV",
        data=st.session_state.ingressos.to_csv(index=False).encode("utf-8-sig"),
        file_name="relatorio_ingressos.csv",
        mime="text/csv"
    )

st.markdown("<p class='rodape'>Clube Olímpico Ingressos • Versão inicial de testes</p>", unsafe_allow_html=True)