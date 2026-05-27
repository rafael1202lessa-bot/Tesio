import streamlit as st
import random
from supabase import create_client, Client

# Configuração da página do Streamlit
st.set_page_config(page_title="Mundo do Textcraft", page_icon="⚔️")

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
    st.session_state.logs = ["Um Orc Selvagem bloqueia o seu caminho!"]

# =====================================================================
# FUNÇÕES DE BANCO DE DADOS
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
        # 1. Cria o usuário no sistema de autenticação
        auth_response = supabase.auth.sign_up({"email": email, "password": senha})
        user_id = auth_response.user.id
        
        # 2. Cria o perfil do usuário na tabela pública
        supabase.table("perfis").insert({"id": user_id, "username": username}).execute()
        st.success("✨ Conta criada com sucesso! Vá para a aba 'Entrar no Jogo'.")
    except Exception as e:
        st.error(f"Erro ao criar conta: {e}")

def carregar_personagem(user_id):
    resposta = supabase.table("personagens").select("*").eq("usuario_id", user_id).execute()
    if resposta.data:
        st.session_state.personagem = resposta.data[0]
    else:
        # Se logou mas não tem personagem, vamos criar um automaticamente para testar
        criar_personagem_padrao(user_id)

def criar_personagem_padrao(user_id):
    novo_p = {
        "usuario_id": user_id,
        "nome": "Herói Iniciante",
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
# INTERFACE DO USUÁRIO (UI)
# =====================================================================
st.title("⚔️ Mundo do Textcraft")

# Tela Inicial (Se não estiver logado)
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
        cad_username = st.text_input("Nome de Usuário (Ex: rafael_lessa)", key="cad_user")
        cad_email = st.text_input("E-mail", key="cad_email")
        cad_senha = st.text_input("Senha (mínimo 6 dígitos)", type="password", key="cad_senha")
        if st.button("Registrar Conta", key="btn_cad"):
            if len(cad_senha) < 6:
                st.warning("A senha precisa ter pelo menos 6 caracteres!")
            elif not cad_username:
                st.warning("Insira um nome de usuário!")
            else:
                criar_conta(cad_email, cad_senha, cad_username)

# Tela do Jogo
elif st.session_state.personagem:
    p = st.session_state.personagem
    
    st.sidebar.header(f"🛡️ {p['nome']}")
    st.sidebar.text(f"Classe: {p['classe']}")
    st.sidebar.text(f"Ouro: {p['ouro']} 🪙")
    
    st.subheader("Status do Combate")
    
    st.caption(f"Seu HP: {p['hp_atual']}/{p['hp_max']}")
    st.progress(max(0.0, min(1.0, p['hp_atual'] / p['hp_max'])))
    
    st.caption(f"Orc Selvagem HP: {st.session_state.orc_hp}/120")
    st.progress(max(0.0, min(1.0, st.session_state.orc_hp / 120)))
    
    st.subheader("Ações de Combate")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💥 Golpe Heroico", disabled=p['hp_atual'] <= 0 or st.session_state.orc_hp <= 0):
            dano_jogador = max(1, p['ataque'] - 5)
            st.session_state.orc_hp -= dano_jogador
            st.session_state.logs.append(f"⚔️ Você causou {dano_jogador} de dano no Orc.")
            
            if st.session_state.orc_hp > 0:
                dano_orc = max(1, 16 - p['defesa'])
                p['hp_atual'] -= dano_orc
                st.session_state.logs.append(f"🪓 O Orc contra-atacou e causou {dano_orc} de dano.")
            else:
                st.session_state.orc_hp = 0
                ouro_ganho = random.randint(5, 15)
                p['ouro'] += ouro_ganho
                p['hp_atual'] = p['hp_max']
                st.session_state.logs.append(f"🎉 Vitória! Você ganhou {ouro_ganho} moedas de ouro.")
                salvar_progresso()
                
            if p['hp_atual'] <= 0:
                p['hp_atual'] = int(p['hp_max'] * 0.5)
                st.session_state.orc_hp = 120
                st.session_state.logs.append("💀 Você ressuscitou no cemitério com metade da vida.")
                salvar_progresso()
                
            st.rerun()

    with col2:
        if st.button("🔄 Procurar Outro Monstro"):
            st.session_state.orc_hp = 120
            st.session_state.logs = ["Um novo Orc aparece bloqueando o caminho!"]
            st.rerun()
            
    st.subheader("Histórico da Batalha")
    for log in reversed(st.session_state.logs[-5:]):
        st.text(log)
        
