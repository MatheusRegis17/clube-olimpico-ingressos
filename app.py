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

VALOR_MESA = 40.0
VALOR_INGRESSO = 10.0
SENHA_GRATUIDADE = "Cata1010#"
USUARIOS_PADRAO = ["Secretaria Lucas", "Secretaria Juliana", "Adm", "Carla Curi"]

MESAS_COLUMNS = ["mesa","status","comprador","telefone","vendedor","pagamento","valor","data_hora","observacao"]
INGRESSOS_COLUMNS = ["comprador","telefone","quantidade","vendedor","pagamento","total","data_hora","observacao"]

st.markdown("""
<style>
.stApp {
    background:
        radial-gradient(circle at top left, rgba(255,153,0,0.10), transparent 28%),
        radial-gradient(circle at top right, rgba(255,70,70,0.08), transparent 24%),
        linear-gradient(180deg, #081326 0%, #091833 35%, #07111f 100%);
}
.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
    max-width: 1200px;
}
.login-card, .hero, .glass-card, .event-card, .map-card {
    background: linear-gradient(135deg, rgba(255,255,255,0.07), rgba(255,255,255,0.03));
    border: 1px solid rgba(255,255,255,0.09);
    box-shadow: 0 18px 42px rgba(0,0,0,0.24);
}
.login-card {
    max-width: 760px;
    margin: 0 auto;
    border-radius: 28px;
    padding: 34px 34px 28px 34px;
}
.hero {
    border-radius: 24px;
    padding: 18px 22px;
    margin-bottom: 18px;
}
.brand-strip {
    margin: 14px auto 10px auto;
    border-radius: 20px;
    padding: 14px 16px;
    background: linear-gradient(90deg, #ff9f0a 0%, #ff6a2f 50%, #ff4747 100%);
    color: white;
    text-align: center;
    box-shadow: 0 12px 24px rgba(255,95,65,0.20);
}
.brand-title {font-size: 28px; font-weight: 900; margin: 0;}
.brand-subtitle {font-size: 14px; margin-top: 2px; opacity: 0.95;}
.title {font-size: 35px; font-weight: 900; color: white; margin: 0;}
.subtitle {font-size: 15px; color: #d8e4ff; margin-top: 4px;}
.glass-card {border-radius: 18px; padding: 16px; margin-bottom: 12px;}
.event-card {border-radius: 18px; padding: 14px; margin-bottom: 16px;}
.map-card {border-radius: 22px; padding: 14px; margin-top: 12px;}
.small-note {font-size: 13px; color: #b9c4de;}
.login-title {
    text-align: center;
    font-size: 30px;
    font-weight: 800;
    color: white;
    margin: 8px 0 6px 0;
}
.login-subtitle {
    text-align: center;
    font-size: 14px;
    color: #c7d2fe;
    margin-bottom: 22px;
}
.logo-wrap {
    display: flex;
    justify-content: center;
    margin-bottom: 8px;
}
.stButton > button {
    border-radius: 14px;
    font-weight: 700;
}
div[data-baseweb="select"] > div {
    border-radius: 14px;
}
input {
    border-radius: 14px !important;
}
.mesa-box {
    border-radius: 12px;
    padding: 10px 6px;
    text-align: center;
    font-weight: 800;
    font-size: 13px;
    margin-bottom: 8px;
    border: 1px solid rgba(255,255,255,0.10);
    box-shadow: 0 6px 14px rgba(0,0,0,0.16);
}
.mesa-disponivel { background: linear-gradient(180deg, #1ea35a, #177c45); color: white; }
.mesa-reservada { background: linear-gradient(180deg, #f5b301, #d99200); color: #1a1a1a; }
.mesa-vendida { background: linear-gradient(180deg, #dc3f45, #b12024); color: white; }
.mesa-cancelada { background: linear-gradient(180deg, #5b6476, #404858); color: white; }
.mesa-gratuidade { background: linear-gradient(180deg, #845ef7, #5f3dc4); color: white; }
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
        img = Image.new('RGBA', (856, 618), (18, 33, 61, 255))
    draw = ImageDraw.Draw(img)
    coords = load_table_coordinates()
    mesa_by_num = {int(m['mesa']): m for m in mesas if str(m.get('mesa','')).isdigit()}
    for item in coords:
        num = int(item['mesa'])
        x = int(item['x'])
        y = int(item['y'])
        mesa = mesa_by_num.get(num, {'status': 'Disponível'})
        color = status_color(mesa['status'])
        rad = 10
        draw.ellipse((x-rad, y-rad, x+rad, y+rad), fill=color, outline='black', width=2)
        # number
        label = str(num)
        offset = 4 if len(label)==1 else 7
        draw.text((x-offset, y-4), label, fill='white')
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

    left_space, center_col, right_space = st.columns([1, 1.6, 1])

    with center_col:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)

        st.markdown('<div class="logo-wrap">', unsafe_allow_html=True)
        show_image(LOGO_CLUBE_PATH, width=140)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(
            '<div class="login-title">Clube Olímpico Ingressos</div>'
            '<div class="login-subtitle">Controle de mesas e ingressos • Festa Junina 2026</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="brand-strip">'
            '<p class="brand-title">Acesso ao sistema</p>'
            '<div class="brand-subtitle">Entre com o usuário já cadastrado ou escolha outro acesso</div>'
            '</div>',
            unsafe_allow_html=True
        )

        if last_user and not st.session_state.force_switch_user:
            usuario = last_user
            st.success("Entrar como: " + usuario)

            with st.form("login_direto"):
                senha = st.text_input("Senha", type="password", placeholder="Digite sua senha")
                entrar = st.form_submit_button("Entrar", use_container_width=True)

            if entrar:
                if hash_password(senha) == users[usuario]['password_hash']:
                    st.session_state.logged_in = True
                    st.session_state.current_user = usuario
                    auth['meta']['last_user'] = usuario
                    save_auth_data(auth)
                    st.rerun()
                else:
                    st.error("Senha incorreta.")

            if st.button("Trocar usuário", use_container_width=True):
                st.session_state.force_switch_user = True
                st.rerun()

        else:
            idx = user_list.index(default_user) if default_user in user_list else 0
            usuario = st.selectbox("Selecione seu acesso", user_list, index=idx)

            tem_senha = bool(users[usuario].get('password_hash',''))

            if tem_senha:
                with st.form("login_escolhido"):
                    senha = st.text_input("Senha", type="password", placeholder="Digite sua senha")
                    entrar = st.form_submit_button("Entrar", use_container_width=True)

                if entrar:
                    if hash_password(senha) == users[usuario]['password_hash']:
                        st.session_state.logged_in = True
                        st.session_state.current_user = usuario
                        auth['meta']['last_user'] = usuario
                        save_auth_data(auth)
                        st.session_state.force_switch_user = False
                        st.rerun()
                    else:
                        st.error("Senha incorreta.")
            else:
                st.warning("Esse usuário está sem senha salva neste servidor.")

                col_a, col_b = st.columns(2)
                if col_a.button("Entrar direto sem senha", use_container_width=True):
                    st.session_state.logged_in = True
                    st.session_state.current_user = usuario
                    auth['meta']['last_user'] = usuario
                    save_auth_data(auth)
                    st.session_state.force_switch_user = False
                    st.rerun()

                with st.expander("Criar ou redefinir senha"):
                    with st.form("criar_senha"):
                        senha_1 = st.text_input("Crie uma senha", type="password")
                        senha_2 = st.text_input("Repita a senha", type="password")
                        criar = st.form_submit_button("Salvar senha", use_container_width=True)
                    if criar:
                        if len(senha_1) < 4:
                            st.error("A senha precisa ter pelo menos 4 caracteres.")
                        elif senha_1 != senha_2:
                            st.error("As senhas não coincidem.")
                        else:
                            users[usuario]['password_hash'] = hash_password(senha_1)
                            auth['meta']['last_user'] = usuario
                            save_auth_data(auth)
                            st.success("Senha salva. Agora você pode entrar.")
                            st.rerun()

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
    return st.radio('Menu', ['Dashboard','Mesas','Ingressos','Relatórios'], horizontal=True, label_visibility='collapsed')


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
    if st.session_state.show_grat_mesa:
        dialog_gratuidade('mesa')
    if st.session_state.show_grat_ingresso:
        dialog_gratuidade('ingresso')
