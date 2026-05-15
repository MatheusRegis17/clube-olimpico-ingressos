import csv
import hashlib
import json
from datetime import datetime
from pathlib import Path
from io import BytesIO

import streamlit as st
from PIL import Image, ImageDraw

st.set_page_config(page_title="Clube Olímpico Ingressos", page_icon="🎟️", layout="wide", initial_sidebar_state="expanded")

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"
USERS_PATH = DATA_DIR / "users.json"
MESAS_PATH = DATA_DIR / "mesas.csv"
INGRESSOS_PATH = DATA_DIR / "ingressos.csv"
MAP_COORDS_PATH = ASSETS_DIR / "mesa_coords.json"
MAP_BACKGROUND_PATH = ASSETS_DIR / "mapa_mesas_base.png"
LOGO_CLUBE_PATH = ASSETS_DIR / "logo_clube.png"
LOGO_ARRAIA_PATH = ASSETS_DIR / "logo_arraia.png"
BACKGROUND_PATH = ASSETS_DIR / "background_festa_junina.png"
CONFIG_PATH = DATA_DIR / "config.json"

VALOR_MESA = 40.0
VALOR_INGRESSO = 10.0
SENHA_GRATUIDADE = "Cata1010#"
USUARIOS_PADRAO = ["Secretaria Lucas", "Secretaria Juliana", "Adm", "Carla Curi"]

MESAS_COLUMNS = ["mesa","status","comprador","telefone","vendedor","pagamento","valor","data_hora","observacao"]
INGRESSOS_COLUMNS = ["comprador","telefone","quantidade","vendedor","pagamento","total","data_hora","observacao"]


def default_config():
    return {
        "background_opacity": 76,
        "background_position": "center center",
        "background_blur": 0,
        "primary_color": "#2f6bff",
        "card_opacity": 90,
        "map_table_width": 32,
        "map_table_height": 20,
    }


def load_config():
    DATA_DIR.mkdir(exist_ok=True)
    if not CONFIG_PATH.exists():
        cfg = default_config()
        CONFIG_PATH.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
        return cfg
    try:
        cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        cfg = default_config()
    base = default_config()
    base.update(cfg)
    return base


def save_config(cfg):
    DATA_DIR.mkdir(exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")


def image_data_uri(path):
    path = Path(path)
    if not path.exists():
        return ""
    try:
        suffix = path.suffix.lower()
        mime = "image/png"
        if suffix in [".jpg", ".jpeg"]:
            mime = "image/jpeg"
        elif suffix == ".webp":
            mime = "image/webp"
        data = base64.b64encode(path.read_bytes()).decode("ascii")
        return f"data:{mime};base64,{data}"
    except Exception:
        return ""


config = load_config()
bg_uri = image_data_uri(BACKGROUND_PATH)
bg_alpha = max(0, min(95, int(config.get("background_opacity", 76)))) / 100
bg_blur = max(0, min(20, int(config.get("background_blur", 0))))
primary_color = config.get("primary_color", "#2f6bff")
card_alpha = max(20, min(98, int(config.get("card_opacity", 90)))) / 100
bg_position = config.get("background_position", "center center")


st.markdown(f"""
<style>
.stApp {{
    background:
      linear-gradient(rgba(4, 10, 20, {bg_alpha}), rgba(4, 10, 20, {min(0.92, bg_alpha + 0.06)})),
      url("{bg_uri}");
    background-size: cover;
    background-position: {bg_position};
    background-attachment: fixed;
    background-repeat: no-repeat;
}}
.stApp::before {{
    content: "";
    position: fixed;
    inset: 0;
    backdrop-filter: blur({bg_blur}px);
    pointer-events: none;
    z-index: -1;
}}
.block-container {{
    padding-top: 1.4rem;
    padding-bottom: 2rem;
    max-width: 1220px;
}}
[data-testid="stHeader"] {{
    background: transparent;
}}
.hero, .glass-card, .event-card, .map-card {{
    background: linear-gradient(135deg, rgba(8,14,28,{card_alpha}), rgba(12,24,48,{max(0.55, card_alpha - 0.12)}));
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 18px;
    box-shadow: 0 18px 46px rgba(0,0,0,0.35);
    backdrop-filter: blur(8px);
}}
.hero {{
    padding: 18px 22px;
    margin-bottom: 18px;
}}
.title {{
    font-size: 34px;
    font-weight: 850;
    color: #ffffff;
    margin: 0;
}}
.subtitle {{
    font-size: 15px;
    color: #dbe7ff;
    margin-top: 4px;
}}
.glass-card {{
    padding: 16px;
    margin-bottom: 12px;
}}
.event-card {{
    padding: 14px;
    margin-bottom: 16px;
}}
.map-card {{
    padding: 14px;
    margin-top: 12px;
}}
.small-note {{
    font-size: 13px;
    color: #dbe7ff;
}}

/* Login */
.login-shell {{
    max-width: 1080px;
    margin: 7vh auto 0 auto;
}}
.login-left {{
    padding: 26px 10px 10px 10px;
}}
.login-logo {{
    display: flex;
    justify-content: flex-start;
    margin-bottom: 16px;
}}
.login-kicker {{
    color: #93c5fd;
    font-size: 12px;
    font-weight: 850;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    margin-bottom: 12px;
}}
.login-title-main {{
    color: #ffffff;
    font-size: 52px;
    font-weight: 900;
    line-height: 1.02;
    margin-bottom: 16px;
    letter-spacing: -0.03em;
}}
.login-desc {{
    color: #dbe7ff;
    font-size: 21px;
    line-height: 1.35;
    max-width: 540px;
    margin-bottom: 22px;
}}
.login-chip-row {{
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}}
.login-chip {{
    display: inline-block;
    padding: 10px 14px;
    background: rgba(255,255,255,0.09);
    border: 1px solid rgba(255,255,255,0.15);
    color: #eef2ff;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 750;
    box-shadow: 0 8px 22px rgba(0,0,0,0.15);
}}
.login-card {{
    background: linear-gradient(160deg, rgba(8, 14, 28, 0.94), rgba(14, 29, 57, 0.90));
    border: 1px solid rgba(255,255,255,0.14);
    border-radius: 24px;
    padding: 26px;
    box-shadow: 0 24px 58px rgba(0,0,0,0.38);
    backdrop-filter: blur(10px);
}}
.login-card-title {{
    color: #ffffff;
    font-size: 27px;
    font-weight: 850;
    text-align: center;
    margin-bottom: 4px;
}}
.login-card-subtitle {{
    color: #dbe7ff;
    font-size: 14px;
    text-align: center;
    margin-bottom: 18px;
}}
.login-note {{
    text-align: center;
    color: #dbe7ff;
    font-size: 14px;
    margin-bottom: 14px;
}}
.login-divider {{
    height: 1px;
    background: rgba(255,255,255,0.12);
    margin: 18px 0;
}}

/* Inputs/buttons */
div[data-testid="stSelectbox"],
div[data-testid="stTextInput"],
div[data-testid="stButton"],
div[data-testid="stForm"],
div[data-testid="stAlert"],
div[data-testid="stExpander"] {{
    width: 100%;
}}
div[data-testid="stSelectbox"] label,
div[data-testid="stTextInput"] label {{
    color: #f8fafc !important;
    font-weight: 700;
}}
div[data-baseweb="select"] > div,
div[data-testid="stTextInput"] input {{
    background: rgba(255,255,255,0.96) !important;
    color: #101828 !important;
    border: 1px solid rgba(255,255,255,0.22) !important;
    border-radius: 13px !important;
    min-height: 50px !important;
    font-size: 16px !important;
}}
div[data-testid="stTextInput"] input::placeholder {{
    color: #667085 !important;
}}
div[data-testid="stFormSubmitButton"] button {{
    background: linear-gradient(180deg, {primary_color}, #174bd6) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 13px !important;
    min-height: 50px !important;
    font-size: 16px !important;
    font-weight: 850 !important;
    box-shadow: 0 12px 24px rgba(47, 107, 255, 0.26);
}}
.stButton > button {{
    border-radius: 13px !important;
    min-height: 46px !important;
    font-weight: 750 !important;
    border: 1px solid rgba(255,255,255,0.18) !important;
    background: rgba(255,255,255,0.08) !important;
    color: #ffffff !important;
}}
.stButton > button:hover {{
    border-color: rgba(255,255,255,0.35) !important;
    background: rgba(255,255,255,0.12) !important;
}}
section[data-testid="stSidebar"] {{
    background: rgba(7,17,31,0.95);
}}
section[data-testid="stSidebar"] * {{
    color: #f8fafc;
}}
h1, h2, h3, h4, h5, h6, p, label, span {{
    color: inherit;
}}

.mesa-box {{
    border-radius: 12px;
    padding: 10px 6px;
    text-align: center;
    font-weight: 800;
    font-size: 13px;
    margin-bottom: 8px;
    border: 1px solid rgba(255,255,255,0.10);
    box-shadow: 0 3px 8px rgba(0,0,0,0.18);
}}
.mesa-disponivel {{ background: linear-gradient(180deg, #1ea35a, #177c45); color: white; }}
.mesa-reservada {{ background: linear-gradient(180deg, #f5b301, #d99200); color: #1a1a1a; }}
.mesa-vendida {{ background: linear-gradient(180deg, #dc3f45, #b12024); color: white; }}
.mesa-cancelada {{ background: linear-gradient(180deg, #5b6476, #404858); color: white; }}
.mesa-gratuidade {{ background: linear-gradient(180deg, #845ef7, #5f3dc4); color: white; }}
</style>
""", unsafe_allow_html=True)


def show_image(path, width=None):
    if Path(path).exists():
        st.image(str(path), width=width)


def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def now_str():
    return datetime.now().strftime('%d/%m/%Y %H:%M:%S')


def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')


def read_csv_rows(path, columns):
    if not path.exists():
        return []
    with path.open('r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        return [{col: row.get(col, '') for col in columns} for row in reader]


def write_csv_rows(path, columns, rows):
    path.parent.mkdir(exist_ok=True)
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({col: row.get(col, '') for col in columns})


def load_auth_data():
    if not USERS_PATH.exists():
        data = {'users': {u: {'password_hash': ''} for u in USUARIOS_PADRAO}, 'meta': {'last_user': ''}}
        USERS_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
        return data
    raw = json.loads(USERS_PATH.read_text(encoding='utf-8'))
    if 'users' not in raw:
        new_raw = {'users': {}, 'meta': {'last_user': ''}}
        for u in USUARIOS_PADRAO:
            if u in raw and isinstance(raw[u], dict):
                new_raw['users'][u] = {'password_hash': raw[u].get('password_hash', '')}
            else:
                new_raw['users'][u] = {'password_hash': ''}
        raw = new_raw
        USERS_PATH.write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding='utf-8')
    raw.setdefault('meta', {})
    raw['meta'].setdefault('last_user', '')
    for u in USUARIOS_PADRAO:
        raw['users'].setdefault(u, {'password_hash': ''})
    return raw


def save_auth_data(data):
    USERS_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def init_files():
    DATA_DIR.mkdir(exist_ok=True)
    auth = load_auth_data()
    save_auth_data(auth)
    if not MESAS_PATH.exists():
        mesas = []
        for i in range(1, 101):
            mesas.append({'mesa': str(i), 'status': 'Disponível', 'comprador': '', 'telefone': '', 'vendedor': '', 'pagamento': '', 'valor': str(VALOR_MESA), 'data_hora': '', 'observacao': ''})
        write_csv_rows(MESAS_PATH, MESAS_COLUMNS, mesas)
    if not INGRESSOS_PATH.exists():
        write_csv_rows(INGRESSOS_PATH, INGRESSOS_COLUMNS, [])


def load_mesas():
    return read_csv_rows(MESAS_PATH, MESAS_COLUMNS)


def save_mesas(rows):
    write_csv_rows(MESAS_PATH, MESAS_COLUMNS, rows)


def load_ingressos():
    return read_csv_rows(INGRESSOS_PATH, INGRESSOS_COLUMNS)


def save_ingressos(rows):
    write_csv_rows(INGRESSOS_PATH, INGRESSOS_COLUMNS, rows)


def refresh_data():
    st.session_state.mesas = load_mesas()
    st.session_state.ingressos = load_ingressos()


def calcular_resumo():
    mesas = st.session_state.mesas
    ingressos = st.session_state.ingressos
    receita_mesas = 0.0
    receita_ingressos = 0.0
    for m in mesas:
        if m['status'] == 'Vendida':
            try: receita_mesas += float(m['valor'])
            except ValueError: pass
    for ing in ingressos:
        try: receita_ingressos += float(ing['total'])
        except ValueError: pass
    return {'disponiveis': sum(1 for m in mesas if m['status']=='Disponível'), 'reservadas': sum(1 for m in mesas if m['status']=='Reservada'), 'vendidas': sum(1 for m in mesas if m['status']=='Vendida'), 'gratuidades': sum(1 for m in mesas if m['status']=='Gratuidade'), 'receita_mesas': receita_mesas, 'receita_ingressos': receita_ingressos, 'receita_total': receita_mesas + receita_ingressos}


def mesa_class(status):
    classes = {'Disponível':'mesa-disponivel', 'Reservada':'mesa-reservada', 'Vendida':'mesa-vendida', 'Cancelada':'mesa-cancelada', 'Gratuidade':'mesa-gratuidade'}
    return classes.get(status, 'mesa-disponivel')


def status_color(status):
    return {'Disponível': '#28c76f', 'Reservada': '#ffb400', 'Vendida': '#ea5455', 'Cancelada': '#6b7280', 'Gratuidade': '#7c3aed'}.get(status, '#28c76f')


def load_table_coordinates():
    if MAP_COORDS_PATH.exists():
        return json.loads(MAP_COORDS_PATH.read_text(encoding='utf-8'))
    return []


def generate_quadra_map(mesas):
    if MAP_BACKGROUND_PATH.exists():
        img = Image.open(MAP_BACKGROUND_PATH).convert('RGBA')
    else:
        img = Image.new('RGBA', (2000, 1414), (18, 33, 61, 255))

    overlay = Image.new('RGBA', img.size, (0,0,0,0))
    draw = ImageDraw.Draw(overlay)
    coords = load_table_coordinates()
    mesa_by_num = {int(m['mesa']): m for m in mesas if str(m.get('mesa','')).isdigit()}

    for item in coords:
        num = int(item['mesa'])
        x = int(item['x'])
        y = int(item['y'])
        mesa = mesa_by_num.get(num, {'status': 'Disponível'})
        color = status_color(mesa['status'])

        box_w, box_h = 32, 20
        draw.rounded_rectangle((x-box_w//2, y-box_h//2, x+box_w//2, y+box_h//2), radius=5,
                               fill=color, outline='white', width=2)
        label = str(num)
        offset = 5 if len(label) == 1 else 9 if len(label) == 2 else 13
        txt_color = 'black' if mesa['status'] == 'Reservada' else 'white'
        draw.text((x-offset, y-7), label, fill=txt_color)

    img = Image.alpha_composite(img, overlay)
    bio = BytesIO()
    img.save(bio, format='PNG')
    return bio.getvalue()

def salvar_mesa(payload, gratuidade=False):
    mesas = load_mesas()
    for mesa in mesas:
        if mesa['mesa'] == str(payload['mesa_numero']):
            if gratuidade:
                mesa['status'] = 'Gratuidade'
                mesa['pagamento'] = 'Gratuidade do Presidente'
                mesa['valor'] = '0.0'
            else:
                mesa['status'] = payload['status']
                mesa['pagamento'] = payload['pagamento']
                mesa['valor'] = '0.0' if payload['status']=='Cancelada' else str(VALOR_MESA)
            mesa['comprador'] = payload['comprador']
            mesa['telefone'] = payload['telefone']
            mesa['vendedor'] = payload['vendedor']
            mesa['data_hora'] = now_str()
            mesa['observacao'] = payload['observacao']
            break
    save_mesas(mesas)
    refresh_data()


def salvar_ingresso(payload, gratuidade=False):
    ingressos = load_ingressos()
    total = 0.0 if gratuidade else float(payload['quantidade']) * VALOR_INGRESSO
    pagamento = 'Gratuidade do Presidente' if gratuidade else payload['pagamento']
    ingressos.append({'comprador': payload['comprador'], 'telefone': payload['telefone'], 'quantidade': str(payload['quantidade']), 'vendedor': payload['vendedor'], 'pagamento': pagamento, 'total': str(total), 'data_hora': now_str(), 'observacao': payload['observacao']})
    save_ingressos(ingressos)
    refresh_data()


@st.dialog('Autorizar gratuidade do presidente')
def dialog_gratuidade(tipo):
    st.write('Digite a senha de autorização do presidente.')
    senha = st.text_input('Senha', type='password')
    c1, c2 = st.columns(2)
    if c1.button('Confirmar', use_container_width=True):
        if senha == SENHA_GRATUIDADE:
            if tipo == 'mesa':
                salvar_mesa(st.session_state.pending_mesa, gratuidade=True)
                st.session_state.pending_mesa = None
                st.session_state.show_grat_mesa = False
            if tipo == 'ingresso':
                salvar_ingresso(st.session_state.pending_ingresso, gratuidade=True)
                st.session_state.pending_ingresso = None
                st.session_state.show_grat_ingresso = False
            st.success('Gratuidade autorizada.')
            st.rerun()
        else:
            st.error('Senha incorreta.')
    if c2.button('Cancelar', use_container_width=True):
        st.session_state.show_grat_mesa = False
        st.session_state.show_grat_ingresso = False
        st.rerun()


def init_session():
    defaults = {'logged_in': False, 'current_user': None, 'pending_mesa': None, 'pending_ingresso': None, 'show_grat_mesa': False, 'show_grat_ingresso': False, 'force_switch_user': False}
    for k,v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v





def login_screen():
    auth = load_auth_data()
    users = auth['users']
    last_user = auth['meta'].get('last_user','')
    user_list = list(users.keys())
    default_user = last_user if last_user in user_list else user_list[0]

    st.markdown('<div class="login-shell">', unsafe_allow_html=True)
    left_col, right_col = st.columns([1.12, 0.88], gap='large')

    with left_col:
        st.markdown('<div class="login-left">', unsafe_allow_html=True)
        st.markdown('<div class="login-logo">', unsafe_allow_html=True)
        show_image(LOGO_CLUBE_PATH, width=110)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-kicker">Sistema oficial do evento</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-title-main">Clube Olímpico<br>Ingressos</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="login-desc">'
            'Controle de mesas e ingressos da Festa Junina do Clube Olímpico de Jacarepaguá, '
            'com acesso identificado para cada vendedor.'
            '</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div class="login-chip-row">'
            '<span class="login-chip">🎪 Festa Junina 2026</span>'
            '<span class="login-chip">📍 Quadra do Clube</span>'
            '<span class="login-chip">🪑 Mesa R$ 40,00</span>'
            '<span class="login-chip">🎫 Ingresso R$ 10,00</span>'
            '</div>',
            unsafe_allow_html=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with right_col:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown('<div class="login-card-title">Acessar sistema</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-card-subtitle">Selecione seu usuário e digite sua senha</div>', unsafe_allow_html=True)

        idx = user_list.index(default_user) if default_user in user_list else 0
        usuario = st.selectbox('Usuário', user_list, index=idx)
        tem_senha = bool(users[usuario].get('password_hash',''))

        if tem_senha:
            with st.form('login_com_usuario_senha'):
                senha = st.text_input('Senha', type='password', placeholder='Digite sua senha')
                entrar = st.form_submit_button('Entrar', use_container_width=True)

            if entrar:
                if hash_password(senha) == users[usuario]['password_hash']:
                    st.session_state.logged_in = True
                    st.session_state.current_user = usuario
                    auth['meta']['last_user'] = usuario
                    save_auth_data(auth)
                    st.session_state.force_switch_user = False
                    st.rerun()
                else:
                    st.error('Senha incorreta.')
        else:
            st.warning('Este usuário ainda não possui senha cadastrada. Cadastre uma senha para entrar.')

            with st.form('criar_primeira_senha'):
                senha_1 = st.text_input('Criar senha', type='password')
                senha_2 = st.text_input('Repetir senha', type='password')
                criar = st.form_submit_button('Cadastrar senha e entrar', use_container_width=True)

            if criar:
                if len(senha_1) < 4:
                    st.error('A senha precisa ter pelo menos 4 caracteres.')
                elif senha_1 != senha_2:
                    st.error('As senhas não coincidem.')
                else:
                    users[usuario]['password_hash'] = hash_password(senha_1)
                    auth['meta']['last_user'] = usuario
                    save_auth_data(auth)
                    st.session_state.logged_in = True
                    st.session_state.current_user = usuario
                    st.session_state.force_switch_user = False
                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

def sidebar():
    with st.sidebar:
        show_image(LOGO_CLUBE_PATH, width=160)
        st.markdown('<div class="event-card">', unsafe_allow_html=True)
        st.markdown('## 🎪 Festa Junina 2026')
        show_image(LOGO_ARRAIA_PATH, width=120)
        st.markdown('📅 **04/07/2026**  \n📍 **Quadra do Clube**  \n🪑 **Mesa:** R$ 40,00  \n🎫 **Ingresso:** R$ 10,00')
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('**Usuário:** ' + str(st.session_state.current_user))
        if st.button('Sair', use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.rerun()


def header():
    left, right = st.columns([0.14, 0.86])
    with left:
        show_image(LOGO_CLUBE_PATH, width=100)
    with right:
        html = '<div class="hero"><p class="title">Clube Olímpico Ingressos</p><p class="subtitle">Sistema de controle de mesas, ingressos e eventos - Usuário: <strong>' + str(st.session_state.current_user) + '</strong></p></div>'
        st.markdown(html, unsafe_allow_html=True)


def menu():
    opcoes = ['Dashboard','Mesas','Ingressos','Relatórios']
    if st.session_state.current_user == 'Adm':
        opcoes.append('Painel Master')
    return st.radio('Menu', opcoes, horizontal=True, label_visibility='collapsed')



def reset_table_coordinates():
    """Distribui 100 mesas: 80 na quadra e 20 na área descoberta."""
    coords = []
    mesa = 1
    left, top, right, bottom = 960, 430, 1655, 1280
    cols, rows = 8, 10
    x_positions = [round(left + i * (right - left) / (cols - 1)) for i in range(cols)]
    y_positions = [round(top + j * (bottom - top) / (rows - 1)) for j in range(rows)]
    for r, y in enumerate(y_positions):
        row_x = x_positions if r % 2 == 0 else list(reversed(x_positions))
        for x in row_x:
            coords.append({"mesa": mesa, "x": int(x), "y": int(y)})
            mesa += 1

    left2, top2, right2, bottom2 = 420, 395, 760, 1170
    cols2, rows2 = 4, 5
    x2 = [round(left2 + i * (right2 - left2) / (cols2 - 1)) for i in range(cols2)]
    y2 = [round(top2 + j * (bottom2 - top2) / (rows2 - 1)) for j in range(rows2)]
    for r, y in enumerate(y2):
        row_x = x2 if r % 2 == 0 else list(reversed(x2))
        for x in row_x:
            coords.append({"mesa": mesa, "x": int(x), "y": int(y)})
            mesa += 1

    MAP_COORDS_PATH.write_text(json.dumps(coords, ensure_ascii=False, indent=2), encoding="utf-8")


def page_dashboard():
    resumo = calcular_resumo()
    st.subheader('📊 Visão geral')
    a,b,c,d = st.columns(4)
    a.metric('Disponíveis', resumo['disponiveis'])
    b.metric('Reservadas', resumo['reservadas'])
    c.metric('Vendidas', resumo['vendidas'])
    d.metric('Gratuidades', resumo['gratuidades'])
    e,f,g = st.columns(3)
    e.metric('Receita mesas', formatar_moeda(resumo['receita_mesas']))
    f.metric('Receita ingressos', formatar_moeda(resumo['receita_ingressos']))
    g.metric('Total geral', formatar_moeda(resumo['receita_total']))
    i1,i2 = st.columns(2)
    with i1:
        st.markdown('<div class="glass-card"><strong>Imagens</strong><br><span class="small-note">As imagens agora ficam na pasta assets e você pode trocar manualmente.</span></div>', unsafe_allow_html=True)
    with i2:
        st.markdown('<div class="glass-card"><strong>Usuário atual</strong><br><span class="small-note">' + str(st.session_state.current_user) + '</span></div>', unsafe_allow_html=True)


def page_mesas():
    mesas = st.session_state.mesas
    st.subheader('🪑 Controle de Mesas')
    st.caption('Mapa baseado na imagem assets/mapa_mesas_base.png e nas coordenadas do arquivo assets/mesa_coords.json.')
    st.markdown('<div class="map-card">', unsafe_allow_html=True)
    st.image(generate_quadra_map(mesas), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.caption('Verde = disponível - Amarelo = reservada - Vermelho = vendida - Roxo = gratuidade - Cinza = cancelada')
    for inicio in range(0, 100, 10):
        cols = st.columns(10)
        for i, col in enumerate(cols):
            idx = inicio + i
            if idx < len(mesas):
                mesa = mesas[idx]
                with col:
                    st.markdown('<div class="mesa-box ' + mesa_class(mesa['status']) + '">Mesa ' + str(mesa['mesa']) + '<br>' + str(mesa['status']) + '</div>', unsafe_allow_html=True)
    st.markdown('---')
    with st.form('form_mesa'):
        c1,c2,c3 = st.columns(3)
        with c1:
            mesa_numero = st.selectbox('Número da mesa', [m['mesa'] for m in mesas])
            comprador = st.text_input('Nome do comprador')
        with c2:
            telefone = st.text_input('Telefone / WhatsApp')
            vendedor = st.text_input('Vendedor', value=st.session_state.current_user)
        with c3:
            status = st.selectbox('Status', ['Reservada','Vendida','Disponível','Cancelada'])
            pagamento = st.selectbox('Forma de pagamento', ['PIX','Dinheiro','Cartão','Pendente','Outro'])
        observacao = st.text_area('Observação')
        gratuidade = st.checkbox('Gratuidade do presidente')
        salvar = st.form_submit_button('Salvar mesa')
    if salvar:
        payload = {'mesa_numero': mesa_numero, 'comprador': comprador, 'telefone': telefone, 'vendedor': vendedor, 'status': status, 'pagamento': pagamento, 'observacao': observacao}
        if gratuidade:
            st.session_state.pending_mesa = payload
            st.session_state.show_grat_mesa = True
            st.rerun()
        else:
            salvar_mesa(payload)
            st.success('Mesa salva.')
            st.rerun()


def page_ingressos():
    st.subheader('🎫 Ingressos Individuais')
    with st.form('form_ingresso'):
        c1,c2,c3 = st.columns(3)
        with c1:
            comprador = st.text_input('Nome do comprador')
            telefone = st.text_input('Telefone / WhatsApp')
        with c2:
            quantidade = st.number_input('Quantidade', min_value=1, step=1)
            vendedor = st.text_input('Vendedor', value=st.session_state.current_user)
        with c3:
            pagamento = st.selectbox('Forma de pagamento', ['PIX','Dinheiro','Cartão','Pendente','Outro'])
            st.info('Total previsto: ' + formatar_moeda(quantidade * VALOR_INGRESSO))
        observacao = st.text_area('Observação')
        gratuidade = st.checkbox('Gratuidade do presidente')
        salvar = st.form_submit_button('Salvar ingresso')
    if salvar:
        payload = {'comprador': comprador, 'telefone': telefone, 'quantidade': quantidade, 'vendedor': vendedor, 'pagamento': pagamento, 'observacao': observacao}
        if gratuidade:
            st.session_state.pending_ingresso = payload
            st.session_state.show_grat_ingresso = True
            st.rerun()
        else:
            salvar_ingresso(payload)
            st.success('Ingresso salvo.')
            st.rerun()
    st.markdown('### Histórico')
    st.dataframe(st.session_state.ingressos, use_container_width=True, hide_index=True)


def rows_to_csv_text(rows, columns):
    output = ','.join(columns) + '\n'
    for row in rows:
        values = []
        for column in columns:
            value = str(row.get(column, '')).replace('"', '""')
            values.append('"' + value + '"')
        output += ','.join(values) + '\n'
    return output


def page_relatorios():
    st.subheader('📑 Relatórios')
    st.markdown('### Mesas')
    st.dataframe(st.session_state.mesas, use_container_width=True, hide_index=True)
    st.download_button('Baixar mesas CSV', rows_to_csv_text(st.session_state.mesas, MESAS_COLUMNS).encode('utf-8-sig'), 'relatorio_mesas.csv', 'text/csv')
    st.markdown('### Ingressos')
    st.dataframe(st.session_state.ingressos, use_container_width=True, hide_index=True)
    st.download_button('Baixar ingressos CSV', rows_to_csv_text(st.session_state.ingressos, INGRESSOS_COLUMNS).encode('utf-8-sig'), 'relatorio_ingressos.csv', 'text/csv')



def save_uploaded_image(uploaded_file, target_path):
    if uploaded_file is None:
        return False
    target_path.parent.mkdir(exist_ok=True)
    img = Image.open(uploaded_file).convert("RGBA")
    img.save(target_path)
    return True


def page_master():
    st.subheader("🛠️ Painel Master")
    st.caption("Área exclusiva do Adm para ajustar aparência, imagens e posições das mesas sem mexer no código.")

    cfg = load_config()

    aba1, aba2, aba3, aba4 = st.tabs(["Aparência", "Imagens", "Mapa das mesas", "Posição das mesas"])

    with aba1:
        st.markdown("### Aparência do sistema")
        col1, col2 = st.columns(2)

        with col1:
            cfg["background_opacity"] = st.slider(
                "Escurecer fundo (%)",
                min_value=0,
                max_value=95,
                value=int(cfg.get("background_opacity", 76)),
                help="Quanto maior, mais escuro fica o fundo para melhorar a leitura."
            )
            cfg["background_blur"] = st.slider(
                "Desfoque do fundo",
                min_value=0,
                max_value=20,
                value=int(cfg.get("background_blur", 0))
            )
            cfg["card_opacity"] = st.slider(
                "Opacidade dos cards (%)",
                min_value=20,
                max_value=98,
                value=int(cfg.get("card_opacity", 90))
            )

        with col2:
            cfg["background_position"] = st.selectbox(
                "Posição do fundo",
                ["center center", "top center", "bottom center", "center left", "center right"],
                index=["center center", "top center", "bottom center", "center left", "center right"].index(cfg.get("background_position", "center center"))
                if cfg.get("background_position", "center center") in ["center center", "top center", "bottom center", "center left", "center right"] else 0
            )
            cfg["primary_color"] = st.color_picker(
                "Cor principal dos botões",
                value=cfg.get("primary_color", "#2f6bff")
            )

        if st.button("Salvar aparência", use_container_width=True):
            save_config(cfg)
            st.success("Aparência salva. Se não atualizar sozinho, use Reboot ou recarregue a página.")
            st.rerun()

    with aba2:
        st.markdown("### Trocar imagens")
        st.info("Envie arquivos PNG/JPG. O sistema salva com o nome correto automaticamente.")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Fundo do sistema**")
            bg = st.file_uploader("Enviar novo fundo", type=["png", "jpg", "jpeg"], key="upload_bg")
            if st.button("Salvar novo fundo", use_container_width=True):
                if save_uploaded_image(bg, BACKGROUND_PATH):
                    st.success("Fundo atualizado.")
                    st.rerun()
                else:
                    st.warning("Escolha uma imagem primeiro.")

            st.markdown("**Logo do Clube**")
            logo = st.file_uploader("Enviar nova logo do clube", type=["png", "jpg", "jpeg"], key="upload_logo")
            if st.button("Salvar logo do clube", use_container_width=True):
                if save_uploaded_image(logo, LOGO_CLUBE_PATH):
                    st.success("Logo do clube atualizada.")
                    st.rerun()
                else:
                    st.warning("Escolha uma imagem primeiro.")

        with col2:
            st.markdown("**Logo do Arraiá**")
            arraia = st.file_uploader("Enviar nova logo do Arraiá", type=["png", "jpg", "jpeg"], key="upload_arraia")
            if st.button("Salvar logo do Arraiá", use_container_width=True):
                if save_uploaded_image(arraia, LOGO_ARRAIA_PATH):
                    st.success("Logo do Arraiá atualizada.")
                    st.rerun()
                else:
                    st.warning("Escolha uma imagem primeiro.")

            st.markdown("**Imagem base do mapa**")
            mapa = st.file_uploader("Enviar nova imagem do mapa", type=["png", "jpg", "jpeg"], key="upload_mapa")
            if st.button("Salvar imagem do mapa", use_container_width=True):
                if save_uploaded_image(mapa, MAP_BACKGROUND_PATH):
                    st.success("Mapa atualizado. Talvez seja necessário ajustar as posições das mesas.")
                    st.rerun()
                else:
                    st.warning("Escolha uma imagem primeiro.")

    with aba3:
        st.markdown("### Prévia do mapa")
        mesas = load_mesas()
        st.image(generate_quadra_map(mesas), use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Recriar posição padrão das 100 mesas", use_container_width=True):
                reset_table_coordinates()
                st.success("Posições padrão recriadas.")
                st.rerun()
        with col2:
            st.download_button(
                "Baixar coordenadas das mesas",
                MAP_COORDS_PATH.read_bytes() if MAP_COORDS_PATH.exists() else b"[]",
                "mesa_coords.json",
                "application/json",
                use_container_width=True
            )

    with aba4:
        st.markdown("### Ajustar mesa individual")
        coords = load_table_coordinates()
        if not coords:
            st.warning("Não encontrei o arquivo de coordenadas. Clique em recriar posição padrão.")
        else:
            mesas_numeros = [int(item["mesa"]) for item in coords]
            mesa_sel = st.selectbox("Mesa", mesas_numeros)
            item = next((i for i in coords if int(i["mesa"]) == int(mesa_sel)), coords[0])

            col1, col2, col3 = st.columns(3)
            with col1:
                x = st.number_input("X", value=int(item["x"]), step=5)
            with col2:
                y = st.number_input("Y", value=int(item["y"]), step=5)
            with col3:
                passo = st.number_input("Passo dos botões", value=10, min_value=1, max_value=100)

            c1, c2, c3, c4 = st.columns(4)
            if c1.button("⬅️ Esquerda", use_container_width=True):
                x -= passo
            if c2.button("➡️ Direita", use_container_width=True):
                x += passo
            if c3.button("⬆️ Subir", use_container_width=True):
                y -= passo
            if c4.button("⬇️ Descer", use_container_width=True):
                y += passo

            if st.button("Salvar posição da mesa", use_container_width=True):
                for i in coords:
                    if int(i["mesa"]) == int(mesa_sel):
                        i["x"] = int(x)
                        i["y"] = int(y)
                        break
                MAP_COORDS_PATH.write_text(json.dumps(coords, ensure_ascii=False, indent=2), encoding="utf-8")
                st.success(f"Mesa {mesa_sel} salva em X={int(x)} / Y={int(y)}.")
                st.rerun()

            st.markdown("### Prévia atualizada")
            st.image(generate_quadra_map(load_mesas()), use_container_width=True)


init_files()
init_session()
refresh_data()

if not st.session_state.logged_in:
    login_screen()
else:
    sidebar()
    header()
    selected = menu()
    if selected == 'Dashboard':
        page_dashboard()
    elif selected == 'Mesas':
        page_mesas()
    elif selected == 'Ingressos':
        page_ingressos()
    elif selected == 'Relatórios':
        page_relatorios()
    elif selected == 'Painel Master':
        page_master()
    if st.session_state.show_grat_mesa:
        dialog_gratuidade('mesa')
    if st.session_state.show_grat_ingresso:
        dialog_gratuidade('ingresso')
