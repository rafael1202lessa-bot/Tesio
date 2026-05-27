import streamlit as st
import random
from supabase import create_client, Client

# Configuração da página do Streamlit
st.set_page_config(page_title="World of Textcraft", page_icon="⚔️")

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
        auth_response = supabase.auth.sin_in_with_password({"email": email, "password": senha})
        st.session_state.user_id = auth_response.user.id
        st.success("Conectado ao reino!")
        carregar_personagem(auth_response.user.id)
    except Exception as e:
        st.error(f"Erro ao entrar: {e}")

def carregar_personagem(user_id):
    resposta = supabase.table("personagens").select("*").eq("usuario_id", user_id).execute()
    if resposta.data:
        st.session_state.personagem = resposta.data[0]
    else:
        st.info("Nenhum personagem encontrado neste usuário.")

def salvar_progresso():
    p = st.session_state.personagem
    supabase.table("personagens").update({
        "hp_atual": p["hp_atual"],
        "ouro": p["ouro"]
    }).eq("id", p["id"]).execute()

# =====================================================================
# INTERFACE DO USUÁRIO (UI)
# =====================================================================
st.title("⚔️ World of Textcraft")

# Tela de Login (Se não estiver logado)
if st.session_state.user_id is None:
    st.subheader("Autenticação do Herói")
    email = st.text_input("E-mail")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar no Jogo"):
        fazer_login(email, senha)

# Tela do Jogo (Se estiver logado e com personagem carregado)
elif st.session_state.personagem:
    p = st.session_state.personagem
    
    # Menu lateral com Status do Jogador
    st.sidebar.header(f"🛡️ {p['nome']}")
    st.sidebar.text(f"Classe: {p['classe']}")
    st.sidebar.text(f"Ouro: {p['ouro']} 🪙")
    
    # Barras de Vida na tela principal
    st.subheader("Status do Combate")
    
    # Barra de HP do Jogador
    st.caption(f"Seu HP: {p['hp_atual']}/{p['hp_max']}")
    st.progress(max(0.0, min(1.0, p['hp_atual'] / p['hp_max'])))
    
    # Barra de HP do Orc
    st.caption(f"Orc Selvagem HP: {st.session_state.orc_hp}/120")
    st.progress(max(0.0, min(1.0, st.session_state.orc_hp / 120)))
    
    # Botões de Ação
    st.subheader("Ações de Combate")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💥 Golpe Heroico", disabled=p['hp_atual'] <= 0 or st.session_state.orc_hp <= 0):
            # Turno do jogador
            dano_jogador = max(1, p['ataque'] - 5)
            st.session_state.orc_hp -= dano_jogador
            st.session_state.logs.append(f"⚔️ Você causou {dano_jogador} de dano no Orc.")
            
            # Turno do Orc (se ele continuar vivo)
            if st.session_state.orc_hp > 0:
                dano_orc = max(1, 16 - p['defesa'])
                p['hp_atual'] -= dano_orc
                st.session_state.logs.append(f"🪓 O Orc contra-atacou e causou {dano_orc} de dano.")
            else:
                st.session_state.orc_hp = 0
                ouro_ganho = random.randint(5, 15)
                p['ouro'] += ouro_ganho
                p['hp_atual'] = p['hp_max'] # Cura para o próximo combate
                st.session_state.logs.append(f"🎉 Vitória! Você ganhou {ouro_ganho} moedas de ouro.")
                salvar_progresso()
                
            # Se o jogador morrer
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
            
    # Histórico de Combate (Log)
    st.subheader("Histórico da Batalha")
    for log in reversed(st.session_state.logs[-5:]): # Mostra os últimos 5 eventos
        st.text(log)
      
