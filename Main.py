import streamlit as st
import random
from supabase import create_client, Client

# Configuração da página do Streamlit
st.set_page_config(page_title="Mundo do Textcraft", page_icon="⚔️", layout="centered")

# =====================================================================
# CONFIGURAÇÃO DO SUPABASE
# =====================================================================
SUPABASE_URL = "https://ldjtqgeyorkzbvuichjj.supabase.co"
SUPABASE_KEY = "sb_publishable_ZWY9Hp6kQrhOzff6xc_DrA_8TlnrqQ_"

@st.cache_resource
def iniciar_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = iniciar_supabase()

# =====================================================================
# ESTADO DA SESSÃO (MEMÓRIA DO JOGO)
# =====================================================================
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "personagem" not in st.session_state:
    st.session_state.personagem = None
if "orc_hp" not in st.session_state:
    st.session_state.orc_hp = 120
if "logs" not in st.session_state:
    st.session_state.logs = ["📢 Um Orc Selvagem bloqueia o seu caminho! Preparar para a batalha!"]

# =====================================================================
# FUNÇÕES DO BANCO DE DADOS
# =====================================================================
def fazer_login(email, senha):
    try:
        auth_response = supabase.auth.sign_in_with_password({"email": email, "password": senha})
        st.session_state.user_id = auth_response.user.id
        st.success("Conectado ao reino!")
        carregar_personagem(auth_response.user.id)
        st.rerun()
    except Exception as e:
        st.error(f"Erro ao entrar: {e}")

def criar_conta(email, senha, username):
    try:
        # Cria o usuário ignorando o envio e o limite de e-mails do provedor
        auth_response = supabase.auth.admin_create_user({
            "email": email,
            "password": senha,
            "email_confirm": True
        })
        user_id = auth_response.user.id
        
        # Insere o nome de usuário na tabela de perfis
        supabase.table("perfis").insert({"id": user_id, "username": username}).execute()
        st.success("✨ Conta criada com sucesso! Mude para a aba '🔒 Entrar no Jogo' para jogar.")
    except Exception as e:
        st.error(f"Erro ao criar conta: {e}")

def carregar_personagem(user_id):
    resposta = supabase.table("personagens").select("*").eq("usuario_id", user_id).execute()
    if resposta.data:
        st.session_state.personagem = resposta.data[0]
    else:
        criar_personagem_padrao(user_id)

def criar_personagem_padrao(user_id):
    novo_p = {
        "usuario_id": user_id, 
        "nome": "Rafael_oficial", 
        "classe": "Guerreiro",
        "hp_max": 150, 
        "hp_atual": 150, 
        "mana_max": 0, 
        "mana_atual": 0,
        "ataque": 25, 
        "magia": 0, 
        "defesa": 10, 
        "ouro": 10
    }
    try:
        insere = supabase.table("personagens").insert(novo_p).execute()
        st.session_state.personagem = insere.data[0]
    except Exception as e:
        st.error(f"Erro ao gerar herói: {e}")

def salvar_progresso():
    p = st.session_state.personagem
    supabase.table("personagens").update({
        "hp_atual": p["hp_atual"], 
        "ouro": p["ouro"]
    }).eq("id", p["id"]).execute()

# =====================================================================
# INTERFACE VISUAL (UI)
# =====================================================================
st.title("⚔️ Mundo do Textcraft")

# TELA INICIAL: LOGIN / CADASTRO
if st.session_state.user_id is None:
    aba_entrar, aba_cadastrar = st.tabs(["🔒 Entrar no Jogo", "📝 Criar Nova Conta"])
    
    with aba_entrar:
        st.subheader("Autenticação do Herói")
        login_email = st.text_input("E-mail", key="login_email")
        login_senha = st.text_input("Senha", type="password", key="login_senha")
        if st.button("Entrar no Jogo", key="btn_login"):
            fazer_login(login_email, login_senha)
            
    with aba_cadastrar:
        st.subheader("Cadastro de Novo Jogador")
        cad_username = st.text_input("Nome de Usuário", key="cad_user")
        cad_email = st.text_input("E-mail", key="cad_email")
        cad_senha = st.text_input("Senha (mínimo 6 dígitos)", type="password", key="cad_senha")
        if st.button("Registrar Conta", key="btn_cad"):
            if len(cad_senha) < 6:
                st.warning("A senha precisa ter pelo menos 6 caracteres!")
            elif not cad_username:
                st.warning("Insira um nome de usuário!")
            else:
                criar_conta(cad_email, cad_senha, cad_username)

# TELA DO JOGO VISUAL
elif st.session_state.personagem:
    p = st.session_state.personagem
    
    # Status na barra lateral
    st.sidebar.markdown(f"### 🛡️ {p['nome']}")
    st.sidebar.markdown(f"**Classe:** {p['classe']}")
    st.sidebar.metric(label="Moedas de Ouro", value=f"{p['ouro']} 🪙")
    
    st.divider()
    
    # ARENA DE COMBATE EM COLUNAS
    col_player, col_vs, col_enemy = st.columns([4, 2, 4])
    
    with col_player:
        st.markdown("<h3 style='text-align: center;'>🧝‍♂️ Você</h3>", unsafe_allow_html=True)
        st.caption(f"HP: {p['hp_atual']} / {p['hp_max']}")
        st.progress(max(0.0, min(1.0, p['hp_atual'] / p['hp_max'])))
        st.markdown(f"<p style='text-align: center;'>🛡️ Defesa: {p['defesa']}<br>⚔️ Ataque: {p['ataque']}</p>", unsafe_allow_html=True)

    with col_vs:
        st.markdown("<h2 style='text-align: center; color: #b30000; padding-top: 20px;'>VS</h2>", unsafe_allow_html=True)

    with col_enemy:
        st.markdown("<h3 style='text-align: center;'>👹 Orc</h3>", unsafe_allow_html=True)
        st.caption(f"HP: {st.session_state.orc_hp} / 120")
        st.progress(max(0.0, min(1.0, st.session_state.orc_hp / 120)))
        st.markdown("<p style='text-align: center;'>🛡️ Defesa: 5<br>🪓 Ataque: 16</p>", unsafe_allow_html=True)

    st.divider()
    
    # BOTÕES DE AÇÃO
    st.markdown("### Escolha sua Próxima Ação")
    btn_col1, btn_col2 = st.columns(2)
    
    with btn_col1:
        if st.button("💥 ATACAR COM GOLPE HEROICO", use_container_width=True, disabled=p['hp_atual'] <= 0 or st.session_state.orc_hp <= 0):
            dano_jogador = max(1, p['ataque'] - 5)
            st.session_state.orc_hp -= dano_jogador
            st.session_state.logs.append(f"⚔️ Você desferiu um golpe e causou {dano_jogador} de dano no Orc!")
            
            if st.session_state.orc_hp > 0:
                dano_orc = max(1, 16 - p['defesa'])
                p['hp_atual'] -= dano_orc
                st.session_state.logs.append(f"🪓 O Orc contra-atacou brandindo o machado e te causou {dano_orc} de dano.")
            else:
                st.session_state.orc_hp = 0
                ouro_ganho = random.randint(5, 15)
                p['ouro'] += ouro_ganho
                p['hp_atual'] = p['hp_max']
                st.session_state.logs.append(f"🏆 VITÓRIA! O Orc caiu. Você pilhou {ouro_ganho} moedas de ouro do corpo dele!")
                salvar_progresso()
                
            if p['hp_atual'] <= 0:
                p['hp_atual'] = int(p['hp_max'] * 0.5)
                st.session_state.orc_hp = 120
                st.session_state.logs.append("💀 Você foi derrotado... O Anjo da Ressurreição te trouxe de volta com metade da vida.")
                salvar_progresso()
                
            st.rerun()

    with btn_col2:
        if st.button("🔄 PROCURAR OUTRO MONSTRO", use_container_width=True):
            st.session_state.orc_hp = 120
            st.session_state.logs = ["🍃 Você caminhou pela floresta e encontrou outro Orc bloqueando a passagem!"]
            st.rerun()
            
    # HISTÓRICO EM CAIXA DE TEXTO
    st.markdown("### 📜 Diário de Combate")
    caixa_texto = ""
    for log in reversed(st.session_state.logs[-6:]):
        caixa_texto += log + "\n\n"
        
    st.text_area(label="Eventos recentes", value=caixa_texto, height=180, label_visibility="collapsed", disabled=True)
            
