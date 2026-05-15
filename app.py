import csv
import hashlib
import json
import base64
from datetime import datetime
from pathlib import Path
from io import BytesIO

import streamlit as st
from streamlit_drawable_canvas import st_canvas
from streamlit_image_coordinates import streamlit_image_coordinates
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
        "background_opacity": 48,
        "background_position": "center center",
        "background_blur": 6,
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
    base = default_config()
    base.update(cfg)
    CONFIG_PATH.write_text(json.dumps(base, ensure_ascii=False, indent=2), encoding="utf-8")


def image_data_uri(path):
    path = Path(path)
    if not path.exists():
        return ""
    suffix = path.suffix.lower()
    mime = "image/png"
    if suffix in [".jpg", ".jpeg"]:
        mime = "image/jpeg"
    elif suffix == ".webp":
        mime = "image/webp"
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}"


def inject_background():
    """Aplica a imagem de fundo usando uma tag <img> fixa atrás do app."""
    cfg = load_config()
    bg_uri_local = image_data_uri(BACKGROUND_PATH)
    if not bg_uri_local:
        return

    opacity = max(0, min(95, int(cfg.get("background_opacity", 38)))) / 100
    blur = max(0, min(20, int(cfg.get("background_blur", 0))))
    position = cfg.get("background_position", "center center")

    # Como este bloco é uma f-string, todas as chaves CSS precisam ser duplicadas.
    st.markdown(
        f"""
        <style>
        .coj-fixed-bg {{
            position: fixed;
            inset: 0;
            width: 100vw;
            height: 100vh;
            object-fit: cover;
            object-position: {position};
            z-index: 0;
            pointer-events: none;
            filter: blur({blur}px);
            transform: scale(1.02);
        }}
        .coj-bg-overlay {{
            position: fixed;
            inset: 0;
            z-index: 0;
            pointer-events: none;
            background:
                linear-gradient(
                    rgba(4,10,20,{opacity}),
                    rgba(4,10,20,{min(0.88, opacity + 0.10)})
                );
        }}

        [data-testid="stAppViewContainer"],
        .stApp {{
            background: transparent !important;
        }}

        [data-testid="stAppViewContainer"] > .main,
        .block-container {{
            position: relative;
            z-index: 2;
        }}

        [data-testid="stHeader"] {{
            background: transparent !important;
            z-index: 3;
        }}

        section[data-testid="stSidebar"] {{
            position: relative;
            z-index: 4;
        }}
        </style>

        <img class="coj-fixed-bg" src="{bg_uri_local}" />
        <div class="coj-bg-overlay"></div>
        """,
        unsafe_allow_html=True,
    )


config = load_config()
bg_uri = image_data_uri(BACKGROUND_PATH)
bg_alpha = max(0, min(95, int(config.get("background_opacity", 30)))) / 100
bg_blur = max(0, min(20, int(config.get("background_blur", 0))))
primary_color = config.get("primary_color", "#2f6bff")
card_alpha = max(20, min(98, int(config.get("card_opacity", 90)))) / 100
bg_position = config.get("background_position", "center center")


st.markdown(f"""
<style>
.stApp {{
    background: transparent !important;
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


inject_background()


def show_image(path, width=None):
    if Path(path).exists():
        st.image(str(path), width=width)


def image_bytes_to_data_uri(image_bytes):
    data = base64.b64encode(image_bytes).decode("ascii")
    return f"data:image/png;base64,{data}"


def show_zoomable_image(image_bytes, zoom_percent=100, height=None):
    """
    Exibe uma imagem com zoom e rolagem.
    zoom_percent acima de 100 aumenta o mapa sem perder a posição.
    """
    zoom_percent = int(zoom_percent)
    zoom_percent = max(50, min(300, zoom_percent))
    data_uri = image_bytes_to_data_uri(image_bytes)
    height_css = f"height:{height}px;" if height else "max-height:78vh;"
    st.markdown(
        f"""
        <div style="
            width:100%;
            {height_css}
            overflow:auto;
            border-radius:18px;
            border:1px solid rgba(255,255,255,0.14);
            background:rgba(0,0,0,0.28);
            padding:10px;
        ">
            <img src="{data_uri}" style="
                width:{zoom_percent}%;
                max-width:none;
                height:auto;
                display:block;
                margin:0 auto;
                border-radius:12px;
            " />
        </div>
        """,
        unsafe_allow_html=True,
    )


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



def table_colors(status):
    """Cores das mesas no mapa."""
    return {
        "Disponível": ("#d99a3a", "#8a5a16", "white"),
        "Reservada": ("#ffb400", "#8a5a16", "black"),
        "Vendida": ("#dc3f45", "#7f1d1d", "white"),
        "Cancelada": ("#6b7280", "#374151", "white"),
        "Gratuidade": ("#7c3aed", "#4c1d95", "white"),
    }.get(status, ("#d99a3a", "#8a5a16", "white"))


def generate_quadra_map(mesas, show_coord_labels=False):
    """
    Gera o mapa usando a planta limpa enviada pelo usuário.
    As 100 mesas são desenhadas dinamicamente em cima da quadra.
    """
    if MAP_BACKGROUND_PATH.exists():
        img = Image.open(MAP_BACKGROUND_PATH).convert("RGBA")
    else:
        img = Image.new("RGBA", (2000, 1414), (18, 33, 61, 255))

    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    coords = load_table_coordinates()
    mesa_by_num = {int(m["mesa"]): m for m in mesas if str(m.get("mesa", "")).isdigit()}
    cfg = load_config()

    radius = int(cfg.get("map_table_radius", 22))
    chair_size = max(5, int(radius * 0.34))

    for item in coords:
        num = int(item["mesa"])
        x = int(item["x"])
        y = int(item["y"])
        mesa = mesa_by_num.get(num, {"status": "Disponível"})
        status = mesa.get("status", "Disponível")
        fill, outline, text_color = table_colors(status)

        # cadeiras nos quatro lados
        draw.rounded_rectangle((x-chair_size//2, y-radius-chair_size-3, x+chair_size//2, y-radius-3),
                               radius=3, fill=outline, outline="white", width=1)
        draw.rounded_rectangle((x-chair_size//2, y+radius+3, x+chair_size//2, y+radius+chair_size+3),
                               radius=3, fill=outline, outline="white", width=1)
        draw.rounded_rectangle((x-radius-chair_size-3, y-chair_size//2, x-radius-3, y+chair_size//2),
                               radius=3, fill=outline, outline="white", width=1)
        draw.rounded_rectangle((x+radius+3, y-chair_size//2, x+radius+chair_size+3, y+chair_size//2),
                               radius=3, fill=outline, outline="white", width=1)

        # mesa redonda
        draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=fill, outline=outline, width=3)

        # círculo branco central para o número
        inner = int(radius * 0.62)
        draw.ellipse((x-inner, y-inner, x+inner, y+inner), fill="white", outline=outline, width=2)

        label = str(num)
        offset = 4 if len(label) == 1 else 8 if len(label) == 2 else 12
        draw.text((x-offset, y-7), label, fill="#111827")

        if show_coord_labels:
            chip_label = str(num)
            chip_w = 18 + (8 * len(chip_label))
            chip_h = 18
            chip_x1 = x - chip_w//2
            chip_y1 = y - radius - chip_h - 8
            chip_x2 = x + chip_w//2
            chip_y2 = y - radius - 8
            draw.rounded_rectangle((chip_x1, chip_y1, chip_x2, chip_y2), radius=6,
                                   fill="#22c55e", outline="white", width=2)
            chip_offset = 4 if len(chip_label) == 1 else 8 if len(chip_label) == 2 else 12
            draw.text((x-chip_offset, chip_y1+3), chip_label, fill="white")

    img = Image.alpha_composite(img, overlay)
    bio = BytesIO()
    img.save(bio, format="PNG")
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
    st.caption('Mapa baseado na planta oficial da quadra. As mesas são desenhadas pelo sistema em cima da imagem.')
    cfg = load_config()
    zoom_mapa = st.slider(
        "Zoom do mapa (%)",
        min_value=50,
        max_value=300,
        value=int(cfg.get("map_zoom", 100)),
        key="zoom_mapa_mesas"
    )
    st.markdown('<div class="map-card">', unsafe_allow_html=True)
    show_zoomable_image(generate_quadra_map(mesas), zoom_percent=zoom_mapa)
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
    img = Image.open(uploaded_file)
    # Padroniza para PNG estável
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGBA")
    img.save(target_path, format="PNG")
    return True


def map_preview_with_selected(mesas, selected_mesa=None, max_width=1050):
    """
    Preview leve para edição.
    Retorna (PIL Image redimensionada, escala_x, escala_y).
    """
    image_bytes = generate_quadra_map(mesas, show_coord_labels=True)
    img = Image.open(BytesIO(image_bytes)).convert("RGBA")

    if selected_mesa is not None:
        coords = load_table_coordinates()
        item = next((i for i in coords if int(i["mesa"]) == int(selected_mesa)), None)
        if item:
            draw = ImageDraw.Draw(img)
            x, y = int(item["x"]), int(item["y"])
            draw.ellipse((x-42, y-42, x+42, y+42), outline="#ffff00", width=6)
            draw.ellipse((x-49, y-49, x+49, y+49), outline="#111827", width=3)

    original_w, original_h = img.size
    if original_w > max_width:
        new_w = max_width
        new_h = int(original_h * (new_w / original_w))
        img_small = img.resize((new_w, new_h))
        scale_x = original_w / new_w
        scale_y = original_h / new_h
        return img_small, scale_x, scale_y

    return img, 1.0, 1.0



def build_canvas_editor_background(mesas, selected_set=None, max_width=1100, map_opacity=48):
    """
    Cria a imagem de fundo do editor visual e os objetos arrastáveis.

    Correção:
    O fundo agora é passado pelo parâmetro background_image do st_canvas,
    em vez de tentar usar "background" dentro do initial_drawing.
    Isso faz o editor aparecer corretamente no Streamlit Cloud.
    """
    selected_set = selected_set or set()
    map_opacity = max(10, min(100, int(map_opacity)))

    if MAP_BACKGROUND_PATH.exists():
        base_original = Image.open(MAP_BACKGROUND_PATH).convert("RGBA")
    else:
        base_original = Image.new("RGBA", (2000, 1414), (18, 33, 61, 255))

    original_w, original_h = base_original.size

    if original_w > max_width:
        canvas_w = int(max_width)
        canvas_h = int(original_h * (canvas_w / original_w))
        scale_x = original_w / canvas_w
        scale_y = original_h / canvas_h
        map_small = base_original.resize((canvas_w, canvas_h))
    else:
        canvas_w, canvas_h = original_w, original_h
        scale_x = 1.0
        scale_y = 1.0
        map_small = base_original

    # Fundo preto + planta transparente
    black_bg = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 255))
    alpha = map_small.getchannel("A")
    alpha = alpha.point(lambda p: int(p * (map_opacity / 100)))
    map_small.putalpha(alpha)
    editor_bg = Image.alpha_composite(black_bg, map_small).convert("RGB")

    coords = load_table_coordinates()
    mesas_status = {int(m["mesa"]): m.get("status", "Disponível") for m in mesas if str(m.get("mesa", "")).isdigit()}
    cfg = load_config()
    radius = int(cfg.get("map_table_radius", 22))

    objects = []
    for item in coords:
        num = int(item["mesa"])
        x = int(item["x"]) / scale_x
        y = int(item["y"]) / scale_y
        status = mesas_status.get(num, "Disponível")
        fill, outline, _ = table_colors(status)
        selected = num in selected_set

        circle_radius = max(11, int(radius / scale_x))
        objects.append({
            "type": "circle",
            "left": x - circle_radius,
            "top": y - circle_radius,
            "radius": circle_radius,
            "fill": "#fff3d7" if not selected else "#fff200",
            "stroke": "#111827" if not selected else "#ff0000",
            "strokeWidth": 2 if not selected else 5,
            "mesa_num": num,
            "selectable": True,
            "hasControls": True,
            "hasBorders": True,
            "lockScalingX": True,
            "lockScalingY": True,
            "lockRotation": True,
        })
        objects.append({
            "type": "text",
            "left": x - (6 if num < 10 else 10 if num < 100 else 14),
            "top": y - 9,
            "text": str(num),
            "fontSize": 16,
            "fontWeight": "bold",
            "fill": "#111827",
            "mesa_num": num,
            "selectable": False,
            "evented": False,
        })

    return editor_bg, canvas_w, canvas_h, scale_x, scale_y, objects


def canvas_positions_signature(canvas_json, scale_x, scale_y):
    """Assinatura simples das posições atuais do canvas para detectar mudanças."""
    if not canvas_json or "objects" not in canvas_json:
        return ""

    circles = [obj for obj in canvas_json.get("objects", []) if obj.get("type") == "circle"]
    parts = []
    for idx, obj in enumerate(circles):
        try:
            radius = float(obj.get("radius", 0))
            left = float(obj.get("left", 0))
            top = float(obj.get("top", 0))
            center_x = int(round((left + radius) * scale_x))
            center_y = int(round((top + radius) * scale_y))
            mesa_num = obj.get("mesa_num", idx + 1)
            parts.append(f"{mesa_num}:{center_x}:{center_y}")
        except Exception:
            pass
    return "|".join(parts)


def save_canvas_positions(canvas_json, scale_x, scale_y):
    """
    Salva posições de todas as mesas movimentadas no canvas.

    Importante:
    O componente pode remover campos personalizados como mesa_num.
    Por isso, se mesa_num não existir no objeto, usamos a ordem dos círculos
    para ligar cada círculo à mesa correspondente.
    """
    if not canvas_json or "objects" not in canvas_json:
        return 0

    coords = load_table_coordinates()
    coords_sorted = sorted(coords, key=lambda x: int(x["mesa"]))
    coords_by_num = {int(item["mesa"]): item for item in coords_sorted}

    circle_objects = [obj for obj in canvas_json.get("objects", []) if obj.get("type") == "circle"]
    moved = 0

    for idx, obj in enumerate(circle_objects):
        # 1) tenta usar mesa_num preservado
        num = obj.get("mesa_num")

        # 2) fallback: se o componente perdeu mesa_num, usa a ordem dos círculos
        if num is None:
            if idx >= len(coords_sorted):
                continue
            num = int(coords_sorted[idx]["mesa"])

        try:
            num = int(num)
            radius = float(obj.get("radius", 0))
            left = float(obj.get("left", 0))
            top = float(obj.get("top", 0))
            center_x_canvas = left + radius
            center_y_canvas = top + radius
            new_x = int(round(center_x_canvas * scale_x))
            new_y = int(round(center_y_canvas * scale_y))
        except Exception:
            continue

        if num in coords_by_num:
            old_x = int(coords_by_num[num]["x"])
            old_y = int(coords_by_num[num]["y"])
            if old_x != new_x or old_y != new_y:
                coords_by_num[num]["x"] = new_x
                coords_by_num[num]["y"] = new_y
                moved += 1

    coords_final = sorted(coords_by_num.values(), key=lambda x: int(x["mesa"]))
    MAP_COORDS_PATH.write_text(json.dumps(coords_final, ensure_ascii=False, indent=2), encoding="utf-8")
    return moved


def move_selected_tables(mesa_nums, dx=0, dy=0):
    coords = load_table_coordinates()
    selected = {int(m) for m in mesa_nums}
    moved = 0
    for item in coords:
        if int(item["mesa"]) in selected:
            item["x"] = int(item["x"]) + int(dx)
            item["y"] = int(item["y"]) + int(dy)
            moved += 1
    MAP_COORDS_PATH.write_text(json.dumps(coords, ensure_ascii=False, indent=2), encoding="utf-8")
    return moved



def selected_table_numbers_from_range(inicio, fim):
    inicio = int(inicio)
    fim = int(fim)
    if inicio > fim:
        inicio, fim = fim, inicio
    return list(range(inicio, fim + 1))


def apply_grid_layout_to_tables(table_nums, start_x, start_y, columns, spacing_x, spacing_y):
    """Organiza as mesas selecionadas em grade."""
    table_nums = [int(n) for n in table_nums]
    if not table_nums:
        return 0

    coords = load_table_coordinates()
    by_num = {int(item["mesa"]): item for item in coords}
    columns = max(1, int(columns))
    moved = 0

    for idx, num in enumerate(table_nums):
        if num not in by_num:
            continue
        row = idx // columns
        col = idx % columns
        new_x = int(start_x + col * spacing_x)
        new_y = int(start_y + row * spacing_y)

        if int(by_num[num]["x"]) != new_x or int(by_num[num]["y"]) != new_y:
            by_num[num]["x"] = new_x
            by_num[num]["y"] = new_y
            moved += 1

    coords_sorted = sorted(by_num.values(), key=lambda x: int(x["mesa"]))
    MAP_COORDS_PATH.write_text(json.dumps(coords_sorted, ensure_ascii=False, indent=2), encoding="utf-8")
    return moved


def move_tables_to_anchor(table_nums, anchor_x, anchor_y):
    """Move o bloco selecionado mantendo o desenho atual."""
    table_nums = [int(n) for n in table_nums]
    if not table_nums:
        return 0

    coords = load_table_coordinates()
    by_num = {int(item["mesa"]): item for item in coords}
    first = table_nums[0]
    if first not in by_num:
        return 0

    old_anchor_x = int(by_num[first]["x"])
    old_anchor_y = int(by_num[first]["y"])
    dx = int(anchor_x) - old_anchor_x
    dy = int(anchor_y) - old_anchor_y

    moved = 0
    for num in table_nums:
        if num not in by_num:
            continue
        by_num[num]["x"] = int(by_num[num]["x"]) + dx
        by_num[num]["y"] = int(by_num[num]["y"]) + dy
        moved += 1

    coords_sorted = sorted(by_num.values(), key=lambda x: int(x["mesa"]))
    MAP_COORDS_PATH.write_text(json.dumps(coords_sorted, ensure_ascii=False, indent=2), encoding="utf-8")
    return moved


def get_table_anchor(table_nums):
    table_nums = [int(n) for n in table_nums]
    coords = load_table_coordinates()
    by_num = {int(item["mesa"]): item for item in coords}
    if not table_nums or table_nums[0] not in by_num:
        return 900, 400
    first = by_num[table_nums[0]]
    return int(first["x"]), int(first["y"])


def get_grid_defaults(table_nums):
    table_nums = [int(n) for n in table_nums]
    if not table_nums:
        return 900, 400, 10, 90, 90

    coords = load_table_coordinates()
    by_num = {int(item["mesa"]): item for item in coords}
    valid = [by_num[n] for n in table_nums if n in by_num]
    if not valid:
        return 900, 400, 10, 90, 90

    min_x = min(int(i["x"]) for i in valid)
    min_y = min(int(i["y"]) for i in valid)

    count = len(valid)
    if count >= 80:
        cols = 10
    elif count >= 40:
        cols = 8
    elif count >= 20:
        cols = 5
    else:
        cols = min(5, count)

    return min_x, min_y, cols, 90, 90


@st.dialog("Editor de bloco de mesas")
def dialog_editor_bloco():
    st.write("Use esta janela para reorganizar várias mesas de uma vez, como um bloco.")

    modo_sel = st.radio(
        "Como selecionar o bloco?",
        ["Intervalo de mesas", "Selecionar manualmente"],
        horizontal=True,
        key="bloco_modo_sel",
    )

    all_nums = [int(item["mesa"]) for item in load_table_coordinates()]

    if modo_sel == "Intervalo de mesas":
        col_i, col_f = st.columns(2)
        with col_i:
            inicio = st.number_input("Mesa inicial", min_value=1, max_value=100, value=1, step=1, key="bloco_inicio")
        with col_f:
            fim = st.number_input("Mesa final", min_value=1, max_value=100, value=20, step=1, key="bloco_fim")
        table_nums = selected_table_numbers_from_range(inicio, fim)
    else:
        table_nums = st.multiselect(
            "Mesas do bloco",
            all_nums,
            default=st.session_state.get("bloco_manual_default", [1, 2, 3, 4, 5]),
            key="bloco_manual",
        )

    st.caption(f"Mesas selecionadas: {len(table_nums)}")

    acao = st.radio(
        "O que você quer fazer?",
        ["Organizar em grade", "Mover bloco mantendo desenho atual"],
        horizontal=False,
        key="bloco_acao",
    )

    if acao == "Organizar em grade":
        default_x, default_y, default_cols, default_sx, default_sy = get_grid_defaults(table_nums)

        c1, c2 = st.columns(2)
        with c1:
            start_x = st.number_input("X inicial do bloco", value=int(default_x), step=10, key="grid_start_x")
            spacing_x = st.number_input("Espaço horizontal entre mesas", value=int(default_sx), step=5, key="grid_spacing_x")
        with c2:
            start_y = st.number_input("Y inicial do bloco", value=int(default_y), step=10, key="grid_start_y")
            spacing_y = st.number_input("Espaço vertical entre mesas", value=int(default_sy), step=5, key="grid_spacing_y")

        columns = st.number_input(
            "Quantidade de colunas do bloco",
            min_value=1,
            max_value=20,
            value=int(default_cols),
            step=1,
            key="grid_columns",
        )

        st.info("Exemplo: se selecionar mesas 1 a 40 e colocar 10 colunas, o sistema cria 4 linhas com 10 mesas.")

        if st.button("Aplicar grade ao bloco", use_container_width=True):
            moved = apply_grid_layout_to_tables(table_nums, start_x, start_y, columns, spacing_x, spacing_y)
            st.success(f"Grade aplicada. Mesas alteradas: {moved}.")
            st.rerun()

    else:
        anchor_x_default, anchor_y_default = get_table_anchor(table_nums)

        c1, c2 = st.columns(2)
        with c1:
            anchor_x = st.number_input("Novo X da primeira mesa do bloco", value=int(anchor_x_default), step=10, key="anchor_x")
        with c2:
            anchor_y = st.number_input("Novo Y da primeira mesa do bloco", value=int(anchor_y_default), step=10, key="anchor_y")

        st.info("O bloco inteiro se move junto, mantendo a posição relativa entre as mesas.")

        if st.button("Mover bloco inteiro", use_container_width=True):
            moved = move_tables_to_anchor(table_nums, anchor_x, anchor_y)
            st.success(f"Bloco movido. Mesas alteradas: {moved}.")
            st.rerun()

    st.markdown("---")
    st.caption("Depois de aplicar, feche a janela e veja a prévia atualizada no Painel Master.")


def page_master():
    if st.session_state.get("current_user") != "Adm":
        st.error("Acesso negado ao Painel Master. Apenas o usuário Adm pode alterar mapa, imagens e aparência.")
        return

    st.subheader("🛠️ Painel Master")
    st.caption("Área exclusiva do Adm para ajustar aparência, imagens e posições das mesas sem mexer no código.")

    cfg = load_config()

    aba1, aba2, aba3, aba4, aba5 = st.tabs(["Aparência", "Imagens", "Mapa das mesas", "Editor visual", "Posição individual"])

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
            cfg["map_table_width"] = st.slider(
                "Largura da marcação das mesas no mapa",
                min_value=24,
                max_value=60,
                value=int(cfg.get("map_table_width", 32))
            )
            cfg["map_table_height"] = st.slider(
                "Altura da marcação das mesas no mapa",
                min_value=16,
                max_value=40,
                value=int(cfg.get("map_table_height", 20))
            )
            cfg["map_table_radius"] = st.slider(
                "Tamanho das mesas no mapa",
                min_value=14,
                max_value=36,
                value=int(cfg.get("map_table_radius", 22))
            )
            cfg["map_zoom"] = st.slider(
                "Zoom padrão do mapa (%)",
                min_value=50,
                max_value=300,
                value=int(cfg.get("map_zoom", 100)),
                help="Controla o tamanho inicial do mapa nas telas de Mesas e Painel Master."
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
            st.success("Aparência salva para esta execução do app. Para deixar permanente após Reboot/redeploy do Streamlit, use o botão de baixar config e suba o arquivo em data/config.json no GitHub.")
            st.rerun()

        st.download_button(
            "Baixar config.json da aparência",
            json.dumps(cfg, ensure_ascii=False, indent=2).encode("utf-8"),
            file_name="config.json",
            mime="application/json",
            use_container_width=True
        )

        with st.expander("Como deixar a aparência permanente após reiniciar"):
            st.markdown("""
            O Streamlit Cloud pode apagar alterações feitas em arquivos quando o app reinicia.

            Para deixar permanente:
            1. ajuste a aparência;
            2. clique em **Salvar aparência**;
            3. clique em **Baixar config.json da aparência**;
            4. no GitHub, substitua o arquivo `data/config.json` por esse arquivo baixado.

            Depois disso, mesmo com Reboot, o app abre com essa aparência.
            """)

    with aba2:
        st.markdown("### Trocar imagens")
        st.caption(f"Status do fundo: {'carregado' if BACKGROUND_PATH.exists() else 'não encontrado'} • Arquivo: assets/background_festa_junina.png")
        st.info("Envie arquivos PNG/JPG. O sistema salva com o nome correto automaticamente.")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Fundo do sistema**")
            st.caption("Depois de salvar, o app recarrega automaticamente. Se necessário, use F5 no navegador.")
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
        if st.button("🧩 Abrir editor de bloco / grade", key="abrir_bloco_mapa_tab", use_container_width=True):
            dialog_editor_bloco()
        mesas = load_mesas()
        zoom_prev = st.slider("Zoom da prévia (%)", 50, 300, int(cfg.get("map_zoom", 100)), key="zoom_preview_master_mapa")
        show_zoomable_image(generate_quadra_map(mesas), zoom_percent=zoom_prev)

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
        st.markdown("### Editor visual das mesas")
        st.info(
            "Modo editor: selecione uma ou várias mesas, arraste no mapa e clique em salvar. "
            "Também dá para mover um grupo usando os botões de direção."
        )

        if st.button("🧩 Abrir editor de bloco / grade", use_container_width=True):
            dialog_editor_bloco()

        coords = load_table_coordinates()
        mesas = load_mesas()

        if not coords:
            st.warning("Não encontrei as coordenadas. Use a aba 'Mapa das mesas' para recriar o padrão.")
        else:
            mesa_nums = [int(item["mesa"]) for item in coords]
            selected_nums = st.multiselect(
                "Mesas selecionadas para destacar ou mover em grupo",
                mesa_nums,
                default=[1],
                help="Você pode selecionar várias mesas e usar os botões de direção para mover todas juntas."
            )

            col_a, col_b, col_c = st.columns([1, 1, 1])
            with col_a:
                editor_width = st.slider(
                    "Tamanho do editor",
                    min_value=700,
                    max_value=1400,
                    value=1050,
                    step=50,
                    help="Aumente se quiser enxergar melhor. Diminua se ficar lento."
                )
            with col_b:
                passo_grupo = st.number_input("Passo do movimento em grupo", min_value=1, max_value=100, value=10)
            with col_c:
                st.caption("Dica: no editor, arraste as bolinhas das mesas. Depois clique em salvar.")

            c1, c2, c3, c4 = st.columns(4)
            if c1.button("⬅️ Mover grupo", use_container_width=True):
                move_selected_tables(selected_nums, dx=-passo_grupo, dy=0)
                st.rerun()
            if c2.button("➡️ Mover grupo", use_container_width=True):
                move_selected_tables(selected_nums, dx=passo_grupo, dy=0)
                st.rerun()
            if c3.button("⬆️ Mover grupo", use_container_width=True):
                move_selected_tables(selected_nums, dx=0, dy=-passo_grupo)
                st.rerun()
            if c4.button("⬇️ Mover grupo", use_container_width=True):
                move_selected_tables(selected_nums, dx=0, dy=passo_grupo)
                st.rerun()

            selected_set = set(selected_nums)

            col_op1, col_op2 = st.columns(2)
            with col_op1:
                map_opacity_editor = st.slider(
                    "Transparência da planta no editor (%)",
                    min_value=10,
                    max_value=100,
                    value=48,
                    step=5,
                    help="Deixe mais baixo para o fundo ficar mais preto; mais alto para enxergar melhor a planta."
                )
            with col_op2:
                auto_save_editor = st.checkbox(
                    "Salvar automaticamente ao soltar mesas",
                    value=False,
                    help="Para evitar travamentos/idas e voltas, deixe desligado e use o botão salvar. Ligue apenas se estiver funcionando leve."
                )

            editor_bg, canvas_w, canvas_h, scale_x, scale_y, objects = build_canvas_editor_background(
                mesas,
                selected_set=selected_set,
                max_width=editor_width,
                map_opacity=map_opacity_editor,
            )

            initial_drawing = {
                "version": "4.4.0",
                "objects": objects,
            }

            # Assinatura da posição salva antes do canvas.
            saved_sig = canvas_positions_signature({"objects": objects}, scale_x, scale_y)
            last_sig_key = "editor_visual_last_saved_signature"
            if st.session_state.get(last_sig_key) in ("", None):
                st.session_state[last_sig_key] = saved_sig

            st.markdown("#### Área de edição")
            st.caption("Se a área abaixo aparecer vazia, clique em 'Recarregar editor'.")
            canvas_key = f"editor_visual_mesas_{st.session_state.get('editor_visual_nonce', 0)}"

            canvas_result = st_canvas(
                fill_color="rgba(255, 243, 215, 0.85)",
                stroke_width=2,
                stroke_color="#111827",
                background_color="#000000",
                background_image=editor_bg,
                height=canvas_h,
                width=canvas_w,
                drawing_mode="transform",
                initial_drawing=initial_drawing,
                update_streamlit=True,
                display_toolbar=False,
                key=canvas_key,
            )

            current_sig = canvas_positions_signature(canvas_result.json_data, scale_x, scale_y) if canvas_result.json_data else ""

            if auto_save_editor and current_sig and current_sig != saved_sig:
                moved = save_canvas_positions(canvas_result.json_data, scale_x, scale_y)
                st.session_state[last_sig_key] = current_sig
                if moved > 0:
                    st.success(f"Salvo automaticamente. Mesas alteradas: {moved}. O mapa principal já foi atualizado.")

            col_save, col_reset = st.columns(2)
            with col_save:
                if st.button("💾 Salvar posições agora", use_container_width=True):
                    moved = save_canvas_positions(canvas_result.json_data, scale_x, scale_y)
                    st.session_state[last_sig_key] = canvas_positions_signature(canvas_result.json_data, scale_x, scale_y)
                    st.success(f"Posições salvas. Mesas alteradas: {moved}. O mapa principal já foi atualizado.")
                    st.rerun()
            with col_reset:
                if st.button("🔄 Recarregar editor a partir do mapa salvo", use_container_width=True):
                    st.session_state[last_sig_key] = ""
                    st.session_state["editor_visual_nonce"] = st.session_state.get("editor_visual_nonce", 0) + 1
                    st.rerun()

            st.caption(
                "O fundo preto com a quadra transparente serve apenas para edição. Depois de salvar, a página Mesas usa a imagem normal do mapa."
            )

    with aba5:
        st.markdown("### Posição individual")
        st.info(
            "Use esta área para ajuste fino de uma mesa específica. "
            "Para edição em massa, use a aba Editor visual."
        )

        coords = load_table_coordinates()
        if not coords:
            st.warning("Não encontrei o arquivo de coordenadas. Clique em recriar posição padrão na aba Mapa das mesas.")
        else:
            mesas_numeros = [int(item["mesa"]) for item in coords]
            mesa_sel = st.selectbox("Mesa para posicionar", mesas_numeros, key="mesa_click_select")
            item = next((i for i in coords if int(i["mesa"]) == int(mesa_sel)), coords[0])

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("X atual", int(item["x"]))
            with col2:
                st.metric("Y atual", int(item["y"]))
            with col3:
                passo = st.number_input("Passo dos botões", value=10, min_value=1, max_value=100)

            st.markdown("#### Ajuste fino")
            c1, c2, c3, c4 = st.columns(4)
            novo_x = int(item["x"])
            novo_y = int(item["y"])

            if c1.button("⬅️ Esquerda", use_container_width=True):
                novo_x -= passo
            if c2.button("➡️ Direita", use_container_width=True):
                novo_x += passo
            if c3.button("⬆️ Subir", use_container_width=True):
                novo_y -= passo
            if c4.button("⬇️ Descer", use_container_width=True):
                novo_y += passo

            if novo_x != int(item["x"]) or novo_y != int(item["y"]):
                for i in coords:
                    if int(i["mesa"]) == int(mesa_sel):
                        i["x"] = int(novo_x)
                        i["y"] = int(novo_y)
                        break
                MAP_COORDS_PATH.write_text(json.dumps(coords, ensure_ascii=False, indent=2), encoding="utf-8")
                st.rerun()

            with st.expander("Edição manual por X e Y"):
                x = st.number_input("X", value=int(item["x"]), step=5)
                y = st.number_input("Y", value=int(item["y"]), step=5)
                if st.button("Salvar X/Y manual", use_container_width=True):
                    for i in coords:
                        if int(i["mesa"]) == int(mesa_sel):
                            i["x"] = int(x)
                            i["y"] = int(y)
                            break
                    MAP_COORDS_PATH.write_text(json.dumps(coords, ensure_ascii=False, indent=2), encoding="utf-8")
                    st.success(f"Mesa {mesa_sel} salva em X={int(x)} / Y={int(y)}.")
                    st.rerun()

            st.markdown("### Prévia atualizada")
            zoom_edit = st.slider("Zoom da prévia de edição (%)", 50, 300, int(load_config().get("map_zoom", 100)), key="zoom_preview_master_edicao_individual")
            show_zoomable_image(generate_quadra_map(load_mesas(), show_coord_labels=True), zoom_percent=zoom_edit)


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
