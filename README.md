import hashlib
import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st


# =========================================================
# CONFIGURAÇÃO GERAL
# =========================================================

st.set_page_config(
    page_title="Clube Olímpico Ingressos",
    page_icon="🎟️",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"

USERS_PATH = DATA_DIR / "users.json"
MESAS_PATH = DATA_DIR / "mesas.csv"
INGRESSOS_PATH = DATA_DIR / "ingressos.csv"

LOGO_CLUBE = ASSETS_DIR / "logo_clube_olimpico.png"
LOGO_EVENTO = ASSETS_DIR / "logo_arraia_coj.png"

VALOR_MESA = 40.0
VALOR_INGRESSO = 10.0
SENHA_GRATUIDADE = "Cata1010#"


# =========================================================
# ESTILO VISUAL
# =========================================================

st.markdown(
    """
    <style>
    .stApp {
        background: radial-gradient(circle at top left, #16213e 0%, #0f172a 38%, #090d16 100%);
    }

    .block-container {
        padding-top: 1.0rem;
        padding-bottom: 2rem;
    }

    .app-header {
        background: linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03));
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 24px;
        padding: 18px 22px;
        margin-bottom: 18px;
        box-shadow: 0 14px 35px rgba(0,0,0,0.20);
    }

    .app-title {
        font-size: 35px;
        font-weight: 900;
        color: white;
        margin: 0;
    }

    .app-subtitle {
        font-size: 15px;
        color: #dbe4ff;
        margin-top: 4px;
    }

    .glass-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02));
        border: 1px solid rgba(255,255,255,0.09);
        border-radius: 20px;
        padding: 16px;
        margin-bottom: 14px;
    }

    .login-shell {
        max-width: 760px;
        margin: 0 auto;
        background: linear-gradient(135deg, rgba(17,24,39,0.97), rgba(30,41,59,0.92));
        border: 1px solid rgba(255,255,255,0.09);
        border-radius: 26px;
        padding: 28px;
        box-shadow: 0 18px 45px rgba(0,0,0,0.28);
    }

    .mesa-box {
        border-radius: 12px;
        padding: 10px 6px;
        text-align: center;
        font-weight: 700;
        font-size: 13px;
        margin-bottom: 8px;
        border: 1px solid rgba(255,255,255,0.10);
        box-shadow: 0 6px 14px rgba(0,0,0,0.15);
    }

    .mesa-disponivel {
        background: linear-gradient(180deg, #1ea35a, #177c45);
        color: white;
    }

    .mesa-reservada {
        background: linear-gradient(180deg, #f5b301, #d99200);
        color: #1a1a1a;
    }

    .mesa-vendida {
        background: linear-gradient(180deg, #dc3f45, #b12024);
        color: white;
    }

    .mesa-cancelada {
        background: linear-gradient(180deg, #5b6476, #404858);
        color: white;
    }

    .mesa-gratuidade {
        background: linear-gradient(180deg, #845ef7, #5f3dc4);
        color: white;
    }

    .subtle-text {
        color: #b8c6e3;
        font-size: 13px;
    }

    div[data-testid="stRadio"] > label {
        color: white;
        font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# FUNÇÕES BÁSICAS
# =========================================================

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def now_str() -> str:
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


def formatar_moeda(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def init_files() -> None:
    DATA_DIR.mkdir(exist_ok=True)

    if not USERS_PATH.exists():
        users = {
            "Secretaria Lucas": {"password_hash": ""},
            "Secretaria Juliana": {"password_hash": ""},
            "Adm": {"password_hash": ""},
            "Carla Curi": {"password_hash": ""},
        }
        USERS_PATH.write_text(json.dumps(users, ensure_ascii=False, indent=2), encoding="utf-8")

    if not MESAS_PATH.exists():
        mesas = pd.DataFrame(
            {
                "mesa": list(range(1, 101)),
                "status": ["Disponível"] * 100,
                "comprador": [""] * 100,
                "telefone": [""] * 100,
                "vendedor": [""] * 100,
                "pagamento": [""] * 100,
                "valor": [VALOR_MESA] * 100,
                "data_hora": [""] * 100,
                "observacao": [""] * 100,
            }
        )
        mesas.to_csv(MESAS_PATH, index=False)

    if not INGRESSOS_PATH.exists():
        ingressos = pd.DataFrame(
            columns=[
                "comprador",
                "telefone",
                "quantidade",
                "vendedor",
                "pagamento",
                "total",
                "data_hora",
                "observacao",
            ]
        )
        ingressos.to_csv(INGRESSOS_PATH, index=False)


def load_users() -> dict:
    return json.loads(USERS_PATH.read_text(encoding="utf-8"))


def save_users(users: dict) -> None:
    USERS_PATH.write_text(json.dumps(users, ensure_ascii=False, indent=2), encoding="utf-8")


def load_mesas() -> pd.DataFrame:
    return pd.read_csv(MESAS_PATH).fillna("")


def save_mesas(df: pd.DataFrame) -> None:
    df.to_csv(MESAS_PATH, index=False)


def load_ingressos() -> pd.DataFrame:
    try:
        return pd.read_csv(INGRESSOS_PATH).fillna("")
    except pd.errors.EmptyDataError:
        return pd.DataFrame(
            columns=[
                "comprador",
                "telefone",
                "quantidade",
                "vendedor",
                "pagamento",
                "total",
                "data_hora",
                "observacao",
            ]
        )


def save_ingressos(df: pd.DataFrame) -> None:
    df.to_csv(INGRESSOS_PATH, index=False)


def refresh_data() -> None:
    st.session_state.mesas_df = load_mesas()
    st.session_state.ingressos_df = load_ingressos()


def calcular_resumo(mesas: pd.DataFrame, ingressos: pd.DataFrame) -> tuple:
    mesas_vendidas = len(mesas[mesas["status"] == "Vendida"])
    mesas_reservadas = len(mesas[mesas["status"] == "Reservada"])
    mesas_disponiveis = len(mesas[mesas["status"] == "Disponível"])
    mesas_gratuidade = len(mesas[mesas["status"] == "Gratuidade"])

    receita_mesas = (
        pd.to_numeric(mesas[mesas["status"] == "Vendida"]["valor"], errors="coerce")
        .fillna(0)
        .sum()
    )

    receita_ingressos = 0.0
    if not ingressos.empty:
        receita_ingressos = pd.to_numeric(ingressos["total"], errors="coerce").fillna(0).sum()

    return (
        mesas_disponiveis,
        mesas_reservadas,
        mesas_vendidas,
        mesas_gratuidade,
        receita_mesas,
        receita_ingressos,
    )


def mesa_class(status: str) -> str:
    classes = {
        "Disponível": "mesa-disponivel",
        "Reservada": "mesa-reservada",
        "Vendida": "mesa-vendida",
        "Cancelada": "mesa-cancelada",
        "Gratuidade": "mesa-gratuidade",
    }
    return classes.get(status, "mesa-disponivel")


# =========================================================
# SALVAMENTO
# =========================================================

def salvar_mesa(payload: dict, gratuidade: bool = False) -> None:
    mesas = load_mesas()
    idx = mesas.index[mesas["mesa"] == int(payload["mesa_numero"])][0]

    if gratuidade:
        status = "Gratuidade"
        pagamento = "Gratuidade do Presidente"
        valor = 0.0
    else:
        status = payload["status"]
        pagamento = payload["pagamento"]
        valor = 0.0 if status == "Cancelada" else VALOR_MESA

    mesas.loc[idx, "status"] = status
    mesas.loc[idx, "comprador"] = payload["comprador"]
    mesas.loc[idx, "telefone"] = payload["telefone"]
    mesas.loc[idx, "vendedor"] = payload["vendedor"]
    mesas.loc[idx, "pagamento"] = pagamento
    mesas.loc[idx, "valor"] = valor
    mesas.loc[idx, "data_hora"] = now_str()
    mesas.loc[idx, "observacao"] = payload["observacao"]

    save_mesas(mesas)
    refresh_data()


def salvar_ingresso(payload: dict, gratuidade: bool = False) -> None:
    ingressos = load_ingressos()

    total = 0.0 if gratuidade else float(payload["quantidade"]) * VALOR_INGRESSO
    pagamento = "Gratuidade do Presidente" if gratuidade else payload["pagamento"]

    nova_linha = pd.DataFrame(
        [
            {
                "comprador": payload["comprador"],
                "telefone": payload["telefone"],
                "quantidade": payload["quantidade"],
                "vendedor": payload["vendedor"],
                "pagamento": pagamento,
                "total": total,
                "data_hora": now_str(),
                "observacao": payload["observacao"],
            }
        ]
    )

    ingressos = pd.concat([ingressos, nova_linha], ignore_index=True)
    save_ingressos(ingressos)
    refresh_data()


# =========================================================
# POPUP GRATUIDADE
# =========================================================

@st.dialog("Autorizar gratuidade do presidente")
def dialog_gratuidade(tipo: str) -> None:
    st.write("Digite a senha de autorização do presidente.")
    senha = st.text_input("Senha", type="password")

    col1, col2 = st.columns(2)

    if col1.button("Confirmar", use_container_width=True):
        if senha == SENHA_GRATUIDADE:
            if tipo == "mesa":
                salvar_mesa(st.session_state.pending_mesa, gratuidade=True)
                st.session_state.pending_mesa = None
                st.session_state.show_grat_mesa = False
                st.success("Gratuidade autorizada.")
                st.rerun()

            if tipo == "ingresso":
                salvar_ingresso(st.session_state.pending_ingresso, gratuidade=True)
                st.session_state.pending_ingresso = None
                st.session_state.show_grat_ingresso = False
                st.success("Gratuidade autorizada.")
                st.rerun()
        else:
            st.error("Senha incorreta.")

    if col2.button("Cancelar", use_container_width=True):
        st.session_state.show_grat_mesa = False
        st.session_state.show_grat_ingresso = False
        st.rerun()


# =========================================================
# LOGIN
# =========================================================

def init_session() -> None:
    defaults = {
        "logged_in": False,
        "current_user": None,
        "pending_mesa": None,
        "pending_ingresso": None,
        "show_grat_mesa": False,
        "show_grat_ingresso": False,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def login_screen() -> None:
    users = load_users()

    col1, col2, col3 = st.columns([0.7, 1.8, 0.7])

    with col2:
        st.markdown('<div class="login-shell">', unsafe_allow_html=True)

        top1, top2 = st.columns([0.38, 0.62])

        with top1:
            if LOGO_CLUBE.exists():
                st.image(str(LOGO_CLUBE), use_container_width=True)

        with top2:
            if LOGO_EVENTO.exists():
                st.image(str(LOGO_EVENTO), use_container_width=True)

        st.markdown("### Acesso ao sistema")
        st.caption("Use um dos acessos autorizados do Clube Olímpico")

        usuario = st.selectbox("Selecione seu acesso", list(users.keys()))
        tem_senha = bool(users[usuario]["password_hash"])

        if not tem_senha:
            st.info("Primeiro acesso. Crie sua senha.")

            with st.form("criar_senha"):
                senha_1 = st.text_input("Crie uma senha", type="password")
                senha_2 = st.text_input("Repita a senha", type="password")
                criar = st.form_submit_button("Criar senha")

            if criar:
                if len(senha_1) < 4:
                    st.error("A senha precisa ter pelo menos 4 caracteres.")
                elif senha_1 != senha_2:
                    st.error("As senhas não coincidem.")
                else:
                    users[usuario]["password_hash"] = hash_password(senha_1)
                    save_users(users)
                    st.success("Senha criada. Agora faça login.")
                    st.rerun()

        else:
            with st.form("login"):
                senha = st.text_input("Senha", type="password")
                entrar = st.form_submit_button("Entrar")

            if entrar:
                if hash_password(senha) == users[usuario]["password_hash"]:
                    st.session_state.logged_in = True
                    st.session_state.current_user = usuario
                    st.rerun()
                else:
                    st.error("Senha incorreta.")

        st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# LAYOUT
# =========================================================

def header() -> None:
    left, right = st.columns([0.18, 0.82])

    with left:
        if LOGO_EVENTO.exists():
            st.image(str(LOGO_EVENTO), use_container_width=True)

    with right:
        st.markdown(
            f"""
            <div class="app-header">
                <p class="app-title">Clube Olímpico Ingressos</p>
                <p class="app-subtitle">
                    Sistema de controle de mesas, ingressos e eventos • Usuário:
                    <strong>{st.session_state.current_user}</strong>
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def sidebar() -> None:
    with st.sidebar:
        if LOGO_CLUBE.exists():
            st.image(str(LOGO_CLUBE), width=180)

        st.markdown("## 🎪 Evento ativo")

        if LOGO_EVENTO.exists():
            st.image(str(LOGO_EVENTO), width=210)

        st.markdown(
            """
            **Festa Junina 2026**  
            📅 04/07/2026  
            📍 Quadra do Clube  
            🪑 Mesa: R$ 40,00  
            🎫 Ingresso: R$ 10,00
            """
        )

        st.markdown("---")
        st.markdown(f"**Usuário:** {st.session_state.current_user}")

        if st.button("Sair", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.rerun()


def menu() -> str:
    return st.radio(
        "Menu",
        ["Dashboard", "Mesas", "Ingressos", "Relatórios"],
        horizontal=True,
        label_visibility="collapsed",
    )


# =========================================================
# PÁGINAS
# =========================================================

def page_dashboard() -> None:
    mesas = st.session_state.mesas_df
    ingressos = st.session_state.ingressos_df

    disp, res, vend, grat, rec_mesas, rec_ing = calcular_resumo(mesas, ingressos)

    st.subheader("📊 Visão geral")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Disponíveis", disp)
    col2.metric("Reservadas", res)
    col3.metric("Vendidas", vend)
    col4.metric("Gratuidades", grat)

    col5, col6, col7 = st.columns(3)
    col5.metric("Receita mesas", formatar_moeda(rec_mesas))
    col6.metric("Receita ingressos", formatar_moeda(rec_ing))
    col7.metric("Total geral", formatar_moeda(rec_mesas + rec_ing))

    info1, info2 = st.columns(2)

    with info1:
        st.markdown(
            """
            <div class="glass-card">
                <strong>Identidade visual aplicada</strong><br>
                <span class="subtle-text">
                    A logo oficial do clube e a arte temática do Arraiá estão integradas ao layout.
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with info2:
        st.markdown(
            f"""
            <div class="glass-card">
                <strong>Usuário atual</strong><br>
                <span class="subtle-text">{st.session_state.current_user}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


def page_mesas() -> None:
    mesas = st.session_state.mesas_df

    st.subheader("🪑 Controle de Mesas")
    st.caption(
        "Verde = disponível • Amarelo = reservada • Vermelho = vendida • "
        "Roxo = gratuidade • Cinza = cancelada"
    )

    for inicio in range(0, 100, 10):
        cols = st.columns(10)

        for i, col in enumerate(cols):
            idx = inicio + i

            if idx < len(mesas):
                row = mesas.iloc[idx]

                with col:
                    st.markdown(
                        f"""
                        <div class="mesa-box {mesa_class(row['status'])}">
                            Mesa {int(row['mesa'])}<br>{row['status']}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    st.markdown("---")

    with st.form("form_mesa"):
        col1, col2, col3 = st.columns(3)

        with col1:
            mesa_numero = st.selectbox("Número da mesa", mesas["mesa"].tolist())
            comprador = st.text_input("Nome do comprador")

        with col2:
            telefone = st.text_input("Telefone / WhatsApp")
            vendedor = st.text_input("Vendedor", value=st.session_state.current_user)

        with col3:
            status = st.selectbox("Status", ["Reservada", "Vendida", "Disponível", "Cancelada"])
            pagamento = st.selectbox("Forma de pagamento", ["PIX", "Dinheiro", "Cartão", "Pendente", "Outro"])

        observacao = st.text_area("Observação")
        gratuidade = st.checkbox("Gratuidade do presidente")
        salvar = st.form_submit_button("Salvar mesa")

    if salvar:
        payload = {
            "mesa_numero": mesa_numero,
            "comprador": comprador,
            "telefone": telefone,
            "vendedor": vendedor,
            "status": status,
            "pagamento": pagamento,
            "observacao": observacao,
        }

        if gratuidade:
            st.session_state.pending_mesa = payload
            st.session_state.show_grat_mesa = True
            st.rerun()
        else:
            salvar_mesa(payload)
            st.success("Mesa salva.")
            st.rerun()


def page_ingressos() -> None:
    ingressos = st.session_state.ingressos_df

    st.subheader("🎫 Ingressos Individuais")

    with st.form("form_ingresso"):
        col1, col2, col3 = st.columns(3)

        with col1:
            comprador = st.text_input("Nome do comprador")
            telefone = st.text_input("Telefone / WhatsApp")

        with col2:
            quantidade = st.number_input("Quantidade", min_value=1, step=1)
            vendedor = st.text_input("Vendedor", value=st.session_state.current_user)

        with col3:
            pagamento = st.selectbox("Forma de pagamento", ["PIX", "Dinheiro", "Cartão", "Pendente", "Outro"])
            st.info(f"Total previsto: {formatar_moeda(quantidade * VALOR_INGRESSO)}")

        observacao = st.text_area("Observação")
        gratuidade = st.checkbox("Gratuidade do presidente")
        salvar = st.form_submit_button("Salvar ingresso")

    if salvar:
        payload = {
            "comprador": comprador,
            "telefone": telefone,
            "quantidade": quantidade,
            "vendedor": vendedor,
            "pagamento": pagamento,
            "observacao": observacao,
        }

        if gratuidade:
            st.session_state.pending_ingresso = payload
            st.session_state.show_grat_ingresso = True
            st.rerun()
        else:
            salvar_ingresso(payload)
            st.success("Ingresso salvo.")
            st.rerun()

    st.dataframe(ingressos, use_container_width=True, hide_index=True)


def page_relatorios() -> None:
    mesas = st.session_state.mesas_df
    ingressos = st.session_state.ingressos_df

    st.subheader("📑 Relatórios")

    st.markdown("### Mesas")
    st.dataframe(mesas, use_container_width=True, hide_index=True)

    st.download_button(
        "Baixar mesas CSV",
        mesas.to_csv(index=False).encode("utf-8-sig"),
        "relatorio_mesas.csv",
        "text/csv",
    )

    st.markdown("### Ingressos")
    st.dataframe(ingressos, use_container_width=True, hide_index=True)

    st.download_button(
        "Baixar ingressos CSV",
        ingressos.to_csv(index=False).encode("utf-8-sig"),
        "relatorio_ingressos.csv",
        "text/csv",
    )


# =========================================================
# EXECUÇÃO DO APP
# =========================================================

init_files()
init_session()
refresh_data()

if not st.session_state.logged_in:
    login_screen()
else:
    sidebar()
    header()

    selected = menu()

    if selected == "Dashboard":
        page_dashboard()
    elif selected == "Mesas":
        page_mesas()
    elif selected == "Ingressos":
        page_ingressos()
    elif selected == "Relatórios":
        page_relatorios()

    if st.session_state.show_grat_mesa:
        dialog_gratuidade("mesa")

    if st.session_state.show_grat_ingresso:
        dialog_gratuidade("ingresso")
