import streamlit as st
from supabase import create_client, Client
import random
import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Silver Tok v2", page_icon="🚀", layout="centered")

# --- CONEXÃO COM SUPABASE ---
url = "https://ldjtqgeyorkzbvuichjj.supabase.co"
key = "sb_publishable_ZWY9Hp6kQrhOzff6xc_DrA_8TlnrqQ_"

try:
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error(f"Erro crítico de conexão: {str(e)}")
    st.stop()

# --- ESTADO DE DESENVOLVIMENTO ---
ESTADO_DESENVOLVIMENTO = True 

# --- INICIALIZAÇÃO DA SESSÃO ---
if "logado" not in st.session_state:
    st.session_state.logado = False
if "user_data" not in st.session_state:
    st.session_state.user_data = None
if "perfil_visitado" not in st.session_state:
    st.session_state.perfil_visitado = None
if "historico_ia" not in st.session_state:
    st.session_state.historico_ia = []

# --- BANCO DE DADOS LOCAL DO CHAT E LIVES (Sessão Ativa) ---
if "chat_privado_salas" not in st.session_state:
    st.session_state.chat_privado_salas = {} 
if "chat_grupos" not in st.session_state:
    st.session_state.chat_grupos = {} 
if "sala_privada_atual" not in st.session_state:
    st.session_state.sala_privada_atual = None
if "codigo_grupo_atual" not in st.session_state:
    st.session_state.codigo_grupo_atual = None
if "live_ativa" not in st.session_state:
    st.session_state.live_ativa = False
if "live_chat" not in st.session_state:
    st.session_state.live_chat = []
if "live_alertas" not in st.session_state:
    st.session_state.live_alertas = []

CODIGO_CORRETO = "ChatPrivado2026"

TITULOS = {
    "rafael_oficial": "👑 Desenvolvedor",
    "rafael_secundario": "⚔️ Vice-Dev",
    "amiga_divulgadora": "📢 Divulgadora",
}

# --- FUNÇÃO PARA SISTEMA DE TEXT-TO-SPEECH (LIVE PIX VOZ ALTA) ---
def emitir_alerta_voz(texto_mensagem):
    """Injeta um script JavaScript discreto para ler a mensagem em voz alta no navegador."""
    js_code = f"""
    <script>
    if ('speechSynthesis' in window) {{
        var msg = new SpeechSynthesisUtterance({repr(texto_mensagem)});
        msg.lang = 'pt-BR';
        msg.rate = 1.1; 
        window.speechSynthesis.speak(msg);
    }}
    </script>
    """
    st.components.v1.html(js_code, height=0, width=0)

# --- FUNÇÃO PARA GERAR ID DE SALA PRIVADA ÚNICA ---
def obter_id_sala_privada(userA, userB):
    return "_".join(sorted([userA, userB]))

# --- FUNÇÃO PARA GERAR SELO E MOLDURA DE PERFIL ---
def aplicar_moldura_e_selo(username, titulo, itens_usuario=None, seguidores=0):
    selo = ""
    if seguidores >= 1000:
        selo += " ⚡[VERIFICADO]"
    if username == "rafael_oficial":
        selo += " ✨[👑 DEV]"
    elif "Dev" in str(titulo) or "Desenvolvedor" in str(titulo):
        selo += " 🛠️[DEV]"
    elif titulo == "🏅 best friends of the dev":
        selo += " 🌟"
        
    estilo_moldura = "border-radius: 50%; object-fit: cover;"
    if itens_usuario and isinstance(itens_usuario, list):
        if "[EQUIPADO] 🖼️ Moldura de Fogo 🔥" in itens_usuario:
            estilo_moldura = "border-radius: 50%; object-fit: cover; border: 4px solid #FF4500; box-shadow: 0 0 15px #FF8C00;"
        elif "[EQUIPADO] 💎 Moldura de Diamante ✨" in itens_usuario:
            estilo_moldura = "border-radius: 50%; object-fit: cover; border: 4px solid #00FFFF; box-shadow: 0 0 15px #00BFFF;"
    return selo, estilo_moldura

# --- SIMULAÇÃO DO SILVER IA ---
def responder_ia(pergunta):
    respostas_prontas = [
        "Com certeza, Rafael! Como seu assistente Silver, estou aqui para ajudar você a gerenciar o Silver Tok. O que mais quer codar hoje?",
        "Essa é uma excelente pergunta. No ecossistema do Silver Tok v2, eu, Silver, recomendo estruturar isso usando Python e Streamlit.",
        "Analisando os dados da plataforma... Pronto! O Silver encontrou a solução: tente postar vídeos curtos com legendas chamativas para alcançar os 1.000 seguidores mais rápido!",
        "Dica do Silver: O Chat EXV foi reformulado com salas privadas, fotos, áudios e grupos por código!",
        "Olá, eu sou o Silver! Posso te ajudar a criar códigos, responder curiosidades ou planejar novas atualizações."
    ]
    return random.choice(respostas_prontas)

# --- FUNÇÕES DE AUTENTICAÇÃO ---
def criar_conta(username, password, nickname, codigo):
    if codigo != CODIGO_CORRETO:
        return "Código de convite inválido!"
    try:
        existe = supabase.table("perfis_usuarios").select("*").eq("username", username).execute()
        if existe.data:
            return "Este nome de usuário já está em uso."
        
        titulo = TITULOS.get(username, "Usuário")
        novo_usuario = {
            "username": username, "senha": password, "nickname": nickname, "titulo": titulo,
            "seguidores": 0, "seguindo": 0, "dinheiro": 0, "verificado": False,
            "foto_perfil": "https://img.icons8.com/colors/150/test-account.png",
            "bio": "Olá! Estou usando o Silver Tok.", "itens_exclusivos": [], "lista_amigos": []
        }
        supabase.table("perfis_usuarios").insert(novo_usuario).execute()
        return "Sucesso"
    except Exception as e:
        return f"Erro ao criar conta: {str(e)}"

# --- TELA DE LOGIN / CADASTRO ---
if not st.session_state.logado:
    st.title("Welcome to Silver Tok v2 🚀")
    aba_login, aba_cadastro = st.tabs(["🔐 Entrar", "📝 Criar Conta"])
    
    with aba_login:
        user_in = st.text_input("Usuário", key="login_user").strip()
        pass_in = st.text_input("Senha", type="password", key="login_pass")
        if st.button("Entrar", use_container_width=True):
            try:
                resultado = supabase.table("perfis_usuarios").select("*").eq("username", user_in).eq("senha", pass_in).execute()
                if resultado.data:
                    st.session_state.logado = True
                    st.session_state.user_data = resultado.data[0]
                    st.rerun()
                else: st.error("Usuário ou senha incorretos.")
            except Exception as e: st.error(f"Erro de conexão com o banco: {str(e)}")
                
    with aba_cadastro:
        new_user = st.text_input("Escolha seu Usuário", key="cad_user").strip()
        new_nick = st.text_input("Nome de Exibição (Nickname)", key="cad_nick")
        new_pass = st.text_input("Escolha sua Senha", type="password", key="cad_pass")
        convite = st.text_input("Código de Convite Secreto", type="password", key="cad_code")
        
        if st.button("Cadastrar Nova Conta", use_container_width=True):
            if not new_user or not new_pass or not new_nick: st.warning("Preencha todos os campos!")
            else:
                status = criar_conta(new_user, new_pass, new_nick, convite)
                if status == "Sucesso": st.success("Conta criada! Faça login ao lado.")
                else: st.error(status)
    st.stop()

def atualizar_sessao():
    try:
        res = supabase.table("perfis_usuarios").select("*").eq("username", st.session_state.user_data['username']).execute()
        if res.data: st.session_state.user_data = res.data[0]
    except: pass

atualizar_sessao()
user_atual = st.session_state.user_data

if user_atual.get("titulo") == "❌ BANIDO":
    st.title("🚫 Conta Bloqueada")
    st.error("Você foi banido deste aplicativo pela administração.")
    st.stop()

if ESTADO_DESENVOLVIMENTO and user_atual.get("titulo") not in ["👑 Desenvolvedor", "🧪 Tester"]:
    st.title("🚧 Aplicativo em Manutenção")
    if st.button("Sair da Conta"):
        st.session_state.logado = False
        st.rerun()
    st.stop()

# --- SIDEBAR (BARRA LATERAL) ---
foto_side = user_atual.get('foto_perfil')
if not foto_side or str(foto_side).strip() in ["0", "None", ""] or not str(foto_side).startswith("http"):
    foto_side = "https://img.icons8.com/colors/150/test-account.png"

meus_itens_sidebar = user_atual.get('itens_exclusivos', [])
if not isinstance(meus_itens_sidebar, list): meus_itens_sidebar = []

selo_sidebar, estilo_da_moldura = aplicar_moldura_e_selo(user_atual.get('username', ''), user_atual.get('titulo', ''), meus_itens_sidebar, user_atual.get('seguidores', 0))

st.sidebar.markdown(f'<img src="{foto_side}" style="{estilo_da_moldura}" width="100">', unsafe_allow_html=True)
st.sidebar.write("") 
st.sidebar.title(f"@{user_atual.get('username', '')}{selo_sidebar}")
st.sidebar.markdown(f"🪙 **Silver Coins:** {user_atual.get('dinheiro', 0)}")
if st.sidebar.button("Sair da Conta"):
    st.session_state.logado = False
    st.rerun()

# --- MENU PRINCIPAL ---
abas = ["📱 Feed", "🎥 Gravar/Postar", "💬 Chat EXV", "🧠 Silver IA", "🛒 Loja do Site", "👤 Meu Perfil"]
if st.session_state.perfil_visitado:
    abas.append("👀 Ver Perfil")
if user_atual.get('username') == "rafael_oficial":
    abas.append("⚡ Painel Dev")

aba_ativa = st.radio("Menu", abas, horizontal=True)
st.write("---")

# --- 1. ABA FEED ---
if aba_ativa == "📱 Feed":
    st.title("📱 Silver Tok")
    termo = st.text_input("🔍 Pesquisar no feed...", "").strip().lower()
    st.write("---")
    
    try:
        req = supabase.table("feed_videos").select("*").order("id", desc=True).execute()
        videos = req.data
    except: videos = []

    for vid in videos:
        v_username = vid.get('username', 'anonimo')
        v_nickname = vid.get('nickname', 'Usuário')
        v_legenda = vid.get('legenda', '')
        v_url = vid.get('url_video', '')
        v_curtidas = vid.get('curtidas', 0)
        v_id = vid.get('id')

        if not termo or termo in v_legenda.lower() or termo in v_username.lower() or termo in v_nickname.lower():
            with st.container():
                foto_autor = "https://img.icons8.com/colors/150/test-account.png"
                titulo_autor = "Usuário"
                itens_autor = []
                seg_autor = 0
                try:
                    autor_req = supabase.table("perfis_usuarios").select("*").eq("username", v_username).execute()
                    if autor_req.data:
                        foto_autor = autor_req.data[0].get('foto_perfil', foto_autor)
                        if not foto_autor or str(foto_autor).strip() in ["0", "None", ""]:
                            foto_autor = "https://img.icons8.com/colors/150/test-account.png"
                        titulo_autor = autor_req.data[0].get('titulo', 'Usuário')
                        itens_autor = autor_req.data[0].get('itens_exclusivos', [])
                        seg_autor = autor_req.data[0].get('seguidores', 0)
                except: pass
                
                selo_post, moldura_post = aplicar_moldura_e_selo(v_username, titulo_autor, itens_autor, seg_autor)
                
                col_foto, col_nome = st.columns([1, 5])
                with col_foto:
                    st.markdown(f'<img src="{foto_autor}" style="{moldura_post}" width="50">', unsafe_allow_html=True)
                with col_nome:
                    if st.button(f"**{v_nickname}** (@{v_username}){selo_post}", key=f"u_{v_id}"):
                        st.session_state.perfil_visitado = v_username
                        st.rerun()
                
                if v_legenda: st.write(v_legenda)
                if v_url:
                    try: st.video(v_url)
                    except: st.error("Vídeo indisponível.")
                
                c1, c2, c3 = st.columns(3)
                with c1:
                    if st.button(f"❤️ {v_curtidas}", key=f"l_{v_id}", use_container_width=True):
                        try:
                            supabase.table("feed_videos").update({"curtidas": v_curtidas + 1}).eq("id", v_id).execute()
                            st.rerun()
                        except: st.error("Erro ao curtir.")
                with c2: st.button("🔗 Copiar", key=f"s_{v_id}", use_container_width=True)
                with c3: abrir_comentarios = st.checkbox("💬 Comentários", key=f"tab_c_{v_id}")
                
                if abrir_comentarios: st.write("**@rafael_oficial:** Esse vídeo ficou brabo! 🔥")
                
                if user_atual.get('username') == v_username or user_atual.get('username') == "rafael_oficial":
                    if st.button(f"🗑️ Apagar Vídeo", key=f"d_{v_id}", use_container_width=True):
                        try:
                            supabase.table("feed_videos").delete().eq("id", v_id).execute()
                            st.rerun()
                        except: st.error("Erro ao apagar.")
                st.write("---")

# --- 2. ABA GRAVAR/POSTAR (ESTÚDIO COM CENTRAL DA LIVE + LIVE PIX TTS) ---
elif aba_ativa == "🎥 Gravar/Postar":
    st.title("🎥 Estúdio de Criação & Live")
    
    aba_upload, aba_link, aba_live = st.tabs([
        "📁 Enviar Vídeo Gravado", 
        "🔗 Postar por Link", 
        "🔴 Central do Streamer (Sua Live)"
    ])
    
    with aba_upload:
        st.subheader("Suba um vídeo da sua galeria")
        legenda_upload = st.text_input("Legenda do seu vídeo:", key="leg_up")
        video_arquivo = st.file_uploader("Selecione o arquivo de vídeo", type=["mp4", "mov", "avi", "webm"])
        
        if st.button("🚀 Publicar Vídeo Gravado", use_container_width=True):
            if not video_arquivo: st.warning("Selecione um arquivo primeiro!")
            else: st.success("Vídeo processado! Integre com o Supabase Storage Bucket para persistência completa.")
                    
    with aba_link:
        legenda = st.text_input("Legenda do post:", key="leg_link")
        url_do_video = st.text_input("Link do vídeo (.mp4):", key="url_mp4")
        if st.button("Publicar Vídeo por Link", use_container_width=True):
            if not url_do_video: st.warning("Insira o link do vídeo.")
            else:
                try:
                    supabase.table("feed_videos").insert({
                        "username": user_atual.get('username'), "nickname": user_atual.get('nickname'),
                        "legenda": legenda, "url_video": url_do_video, "curtidas": 0
                    }).execute()
                    st.success("Publicado no Feed!")
                except Exception as e: st.error(f"Erro ao publicar: {str(e)}")
                    
    with aba_live:
        st.subheader("📹 Painel de Controle de Transmissão")
        
        if not st.session_state.live_ativa:
            titulo_live = st.text_input("Título da sua Live:", placeholder="Ex: Jogando com inscritos! 🔥")
            if st.button("🔴 INICIAR LIVE", use_container_width=True):
                if titulo_live:
                    st.session_state.live_ativa = True
                    st.session_state.live_chat = [{"remetente": "Sistema", "conteudo": f"Sua live '{titulo_live}' foi iniciada!"}]
                    st.session_state.live_alertas = []
                    st.rerun()
                else: st.warning("Insira um título para começar.")
        else:
            st.success("🎥 VOCÊ ESTÁ AO VIVO!")
            if st.button("⏹️ Encerrar Transmissão", use_container_width=True):
                st.session_state.live_ativa = False
                st.rerun()
            
            st.write("---")
            col_video_retorno, col_chat_live = st.columns([4, 3])
            
            with col_video_retorno:
                st.markdown("### 🖥️ Retorno do seu Vídeo")
                # Exibe a câmera do desenvolvedor na tela para ver o próprio enquadramento
                st.camera_input("Monitor da Câmera", key="monitor_live_cam")
                
                st.markdown("### 🪙 Últimos Alertas Live Pix (Voz Alta)")
                for alerta in st.session_state.live_alertas[-3:]:
                    st.warning(f"🎁 **{alerta['usuario']}** enviou **{alerta['moedas']} Silver Coins**:\n*{alerta['msg']}*")
            
            with col_chat_live:
                st.markdown("### 💬 Chat da Live")
                
                # Container scannável de chat da transmissão
                with st.container(border=True, height=250):
                    for msg_l in st.session_state.live_chat:
                        st.write(f"**@{msg_l['remetente']}:** {msg_l['conteudo']}")
                
                # Simulador de Interatividade da audiência (Para o Dev testar o Live Pix)
                st.write("---")
                st.caption("🧪 Simulador de Público (Modo Dev)")
                sim_user = st.text_input("Usuário do fã:", value="seguidor_vip_01", key="sim_u")
                sim_txt = st.text_input("Mensagem do Chat:", placeholder="Manda salve Rafa!", key="sim_t")
                
                c_b1, c_b2 = st.columns(2)
                with c_b1:
                    if st.button("💬 Simular Mensagem", use_container_width=True):
                        if sim_txt:
                            st.session_state.live_chat.append({"remetente": sim_user, "conteudo": sim_txt})
                            st.rerun()
                with c_b2:
                    sim_coins = st.number_input("Moedas:", min_value=10, value=50, step=10)
                    if st.button("🎁 Simular Silver Coins", use_container_width=True):
                        if sim_txt:
                            # Adiciona no chat
                            texto_completo_alerta = f"Enviou {sim_coins} Silver Coins! Mensagem: {sim_txt}"
                            st.session_state.live_chat.append({"remetente": sim_user, "conteudo": f"⭐ {texto_completo_alerta}"})
                            
                            # Registra o alerta estruturado
                            st.session_state.live_alertas.append({"usuario": sim_user, "moedas": sim_coins, "msg": sim_txt})
                            
                            # DISPARA A LEITURA EM VOZ ALTA DO LIVE PIX
                            texto_leitura = f"{sim_user} enviou {sim_coins} Silver Coins. {sim_txt}"
                            emitir_alerta_voz(texto_leitura)
                            st.rerun()

# --- 3. ABA CHAT EXV ---
elif aba_ativa == "💬 Chat EXV":
    st.title("💬 Chat EXV")
    aba_dm, aba_grp = st.tabs(["🔒 Conversas Privadas (Salas)", "👥 Grupos por Código"])
    
    with aba_dm:
        try:
            todos_req = supabase.table("perfis_usuarios").select("username, nickname").execute()
            lista_usuarios = [u for u in todos_req.data if u['username'] != user_atual.get('username')]
        except: lista_usuarios = []
        
        st.subheader("🔒 Suas Salas Privadas Ativas")
        if lista_usuarios:
            opcoes_usuarios = {u['username']: f"{u['nickname']} (@{u['username']})" for u in lista_usuarios}
            usuario_selecionado = st.selectbox("Abrir sala privada com:", list(opcoes_usuarios.keys()), format_func=lambda x: opcoes_usuarios[x])
            
            if st.button("🚪 Entrar na Sala Privada", use_container_width=True):
                st.session_state.sala_privada_atual = obter_id_sala_privada(user_atual.get('username'), usuario_selecionado)
                st.session_state.codigo_grupo_atual = None
        
        if st.session_state.sala_privada_atual:
            sala_id = st.session_state.sala_privada_atual
            outro_usuario = sala_id.replace(user_atual.get('username'), "").replace("_", "")
            
            st.write("---")
            st.markdown(f"### 💬 Sala Privada: **@{user_atual.get('username')}** & **@{outro_usuario}**")
            
            if sala_id not in st.session_state.chat_privado_salas:
                st.session_state.chat_privado_salas[sala_id] = []
                
            for msg in st.session_state.chat_privado_salas[sala_id]:
                with st.chat_message("user" if msg['remetente'] == user_atual.get('username') else "assistant"):
                    st.markdown(f"**@{msg['remetente']}**")
                    if msg['tipo'] == 'texto': st.write(msg['conteudo'])
                    elif msg['tipo'] == 'foto': st.image(msg['conteudo'], caption="Foto enviada", width=250)
                    elif msg['tipo'] == 'audio': st.audio(msg['conteudo'])
            
            st.write("---")
            tipo_midia = st.radio("O que quer enviar?", ["📝 Mensagem", "🖼️ Link de Foto", "🎵 Link de Áudio"], horizontal=True)
            
            if tipo_midia == "📝 Mensagem":
                txt = st.text_input("Sua mensagem:", key="msg_p_input")
                if st.button("Enviar Texto", use_container_width=True) and txt:
                    st.session_state.chat_privado_salas[sala_id].append({"remetente": user_atual.get('username'), "tipo": "texto", "conteudo": txt})
                    st.rerun()
            elif tipo_midia == "🖼️ Link de Foto":
                img_url = st.text_input("URL da Imagem (.jpg, .png):", placeholder="https://exemplo.com/imagem.png")
                if st.button("Enviar Foto", use_container_width=True) and img_url:
                    st.session_state.chat_privado_salas[sala_id].append({"remetente": user_atual.get('username'), "tipo": "foto", "conteudo": img_url})
                    st.rerun()
            elif tipo_midia == "🎵 Link de Áudio":
                audio_url = st.text_input("URL do arquivo de áudio (.mp3, .wav):", placeholder="https://exemplo.com/audio.mp3")
                if st.button("Enviar Áudio", use_container_width=True) and audio_url:
                    st.session_state.chat_privado_salas[sala_id].append({"remetente": user_atual.get('username'), "tipo": "audio", "conteudo": audio_url})
                    st.rerun()
                    
            if st.button("❌ Fechar Sala Privada", use_container_width=True):
                st.session_state.sala_privada_atual = None
                st.rerun()

    with aba_grp:
        st.subheader("👥 Grupos Protegidos por Código")
        cg1, cg2 = st.columns(2)
        with cg1:
            st.markdown("### Criar Novo Grupo")
            nome_novo_grp = st.text_input("Nome do Grupo:")
            cod_novo_grp = st.text_input("Criar Código de Acesso Secreto:", type="password", key="new_grp_cod")
            if st.button("🏗️ Gerar Sala de Grupo", use_container_width=True):
                if nome_novo_grp and cod_novo_grp:
                    st.session_state.chat_grupos[cod_novo_grp] = {"nome": nome_novo_grp, "mensagens": []}
                    st.success(f"Grupo '{nome_novo_grp}' criado!")
                else: st.warning("Preencha todos os campos do grupo.")
                
        with cg2:
            st.markdown("### Entrar em um Grupo")
            cod_inserido = st.text_input("Digitar Código de Acesso do Grupo:", type="password", key="join_grp_cod")
            if st.button("🚪 Entrar no Grupo", use_container_width=True):
                if cod_inserido in st.session_state.chat_grupos:
                    st.session_state.codigo_grupo_atual = cod_inserido
                    st.session_state.sala_privada_atual = None
                    st.success(f"Conectado ao grupo: {st.session_state.chat_grupos[cod_inserido]['nome']}")
                else: st.error("Código de grupo incorreto ou inexistente!")
                
        if st.session_state.codigo_grupo_atual:
            cod_g = st.session_state.codigo_grupo_atual
            dados_grupo = st.session_state.chat_grupos[cod_g]
            
            st.write("---")
            st.markdown(f"### 👥 Sala de Grupo Ativa: **{dados_grupo['nome']}**")
            
            for m_g in dados_grupo['mensagens']:
                with st.chat_message("user" if m_g['remetente'] == user_atual.get('username') else "assistant"):
                    st.write(f"**@{m_g['remetente']}:** {m_g['conteudo']}")
                    
            msg_para_enviar_grp = st.text_input("Escrever no grupo...", key="input_msg_grp")
            if st.button("Enviar para o Grupo", use_container_width=True) and msg_para_enviar_grp:
                st.session_state.chat_grupos[cod_g]['mensagens'].append({"remetente": user_atual.get('username'), "conteudo": msg_para_enviar_grp})
                st.rerun()
                
            if st.button("❌ Sair do Grupo", use_container_width=True):
                st.session_state.codigo_grupo_atual = None
                st.rerun()

# --- 4. ABA SILVER IA ---
elif aba_ativa == "🧠 Silver IA":
    st.title("🧠 Silver IA")
    st.write("Olá! Eu sou o **Silver**, seu assistente oficial do Silver Tok v2.")
    
    prompt_usuario = st.text_input("O que deseja saber ou pesquisar?", placeholder="Ex: Me dê ideias de vídeos para o meu feed")
    if st.button("Perguntar ao Silver", use_container_width=True):
        if prompt_usuario:
            resposta = responder_ia(prompt_usuario)
            st.session_state.historico_ia.insert(0, {"pergunta": prompt_usuario, "resposta": resposta})
            
    if st.session_state.historico_ia:
        st.write("---")
        st.subheader("💬 Histórico de Conversas")
        for chat in st.session_state.historico_ia:
            st.info(f"❓ **Você:** {chat['pergunta']}")
            st.success(f"🤖 **Silver:** {chat['resposta']}")

# --- 5. ABA LOJA DO SITE (ATUALIZADA COM SILVER COINS) ---
elif aba_ativa == "🛒 Loja do Site":
    st.title("🛒 Loja de Customizações e Vantagens")
    st.write(f"🪙 **Sua Carteira:** {user_atual.get('dinheiro', 0)} Silver Coins")
    st.write("---")

    customizacoes = {
        "🖼️ Moldura de Fogo 🔥": 1000, "💎 Moldura de Diamante ✨": 2500,
        "🖼️ Banner Estelar (Perfil)": 1500, "💬 Caixa de Texto Neon (Feed)": 2000, "🌈 Nickname Dourado": 5000
    }

    for item, preco in customizacoes.items():
        with st.container():
            col_info, col_btn = st.columns([3, 1])
            with col_info:
                st.markdown(f"### {item}")
                st.markdown(f"🪙 Custo: **{preco} Silver Coins**")
            with col_btn:
                st.write("<br>", unsafe_allow_html=True)
                meus_visuais = user_atual.get('itens_exclusivos', [])
                if not isinstance(meus_visuais, list): meus_visuais = []
                
                if item in meus_visuais or f"[EQUIPADO] {item}" in meus_visuais:
                    st.button("✅ Adquirido", key=f"loja_{item}", disabled=True, use_container_width=True)
                else:
                    if st.button(f"🛒 Adquirir", key=f"comprar_{item}", use_container_width=True):
                        saldo = user_atual.get('dinheiro', 0)
                        if saldo >= preco:
                            try:
                                novo_saldo = saldo - preco
                                meus_visuais.append(item)
                                supabase.table("perfis_usuarios").update({"dinheiro": novo_saldo, "itens_exclusivos": meus_visuais}).eq("username", user_atual.get('username')).execute()
                                st.success(f"🎉 '{item}' adquirido!")
                                st.rerun()
                            except: st.error("Erro ao realizar compra.")
                        else: st.error("❌ Saldo de Silver Coins insuficiente!")
            st.write("---")

# --- 6. ABA MEU PERFIL ---
elif aba_ativa == "👤 Meu Perfil":
    meus_itens_perfil = user_atual.get('itens_exclusivos', [])
    if not isinstance(meus_itens_perfil, list): meus_itens_perfil = []
        
    selo_meu_perfil, moldura_meu_perfil = aplicar_moldura_e_selo(user_atual.get('username'), user_atual.get('titulo'), meus_itens_perfil, user_atual.get('seguidores', 0))
    
    col_foto, col_stats = st.columns([1, 2])
    with col_foto:
        f_perfil = user_atual.get('foto_perfil')
        if not f_perfil or str(f_perfil).strip() in ["0", "None", ""] or not str(f_perfil).startswith("http"):
            f_perfil = "https://img.icons8.com/colors/150/test-account.png"
        st.markdown(f'<img src="{f_perfil}" style="{moldura_meu_perfil}" width="140">', unsafe_allow_html=True)
            
    with col_stats:
        st.header(f"{user_atual.get('nickname', 'Usuário')}{selo_meu_perfil}")
        st.write(f"**@{user_atual.get('username', '')}** | {user_atual.get('titulo', 'Usuário')}")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Seguidores", user_atual.get('seguidores', 0))
        c2.metric("Seguindo", user_atual.get('seguindo', 0))
        c3.metric("Coins", f"{user_atual.get('dinheiro', 0)}")
    
    st.write(f"📝 **Bio:** {user_atual.get('bio', 'Disponível')}")
    st.write("---")
    
    exp_seg = st.expander("👥 Ver Meus Seguidores / Amigos")
    with exp_seg:
        st.markdown("### ➕ Adicionar Novo Amigo/Seguidor")
        amigo_para_add = st.text_input("Digite o @username exato do seguidor:", key="input_add_amigo_perfil").strip()
        if st.button("➕ Adicionar na Lista", use_container_width=True):
            if amigo_para_add:
                try:
                    checar_user = supabase.table("perfis_usuarios").select("username").eq("username", amigo_para_add).execute()
                    if checar_user.data:
                        lista_amigos_perfil = user_atual.get('lista_amigos', [])
                        if not isinstance(lista_amigos_perfil, list): lista_amigos_perfil = []
                        
                        if amigo_para_add in lista_amigos_perfil: st.warning("Este usuário já está na sua lista!")
                        else:
                            lista_amigos_perfil.append(amigo_para_add)
                            supabase.table("perfis_usuarios").update({"lista_amigos": lista_amigos_perfil}).eq("username", user_atual.get('username')).execute()
                            st.success(f"🎉 @{amigo_para_add} adicionado com sucesso!")
                            st.rerun()
                    else: st.error("Usuário não encontrado no Silver Tok.")
                except: st.error("Erro ao processar adição de amigo.")
            else: st.warning("Por favor, digite um nome de usuário.")

        st.write("---")
        lista_amigos_perfil = user_atual.get('lista_amigos', [])
        if lista_amigos_perfil and isinstance(lista_amigos_perfil, list):
            for amg in lista_amigos_perfil:
                col_amg_nome, col_amg_btn = st.columns([3, 2])
                with col_amg_nome: st.write(f"👤 **@{amg}**")
                with col_amg_btn:
                    if st.button(f"💬 Conversa com Seguidor", key=f"chat_seg_{amg}", use_container_width=True):
                        st.session_state.sala_privada_atual = obter_id_sala_privada(user_atual.get('username'), amg)
                        st.session_state.codigo_grupo_atual = None
                        st.rerun()
        else: st.caption("Nenhum seguidor ou amigo adicionado ainda.")
    
    st.write("---")
    st.subheader("🎒 Meu Inventário Visual")
    if meus_itens_perfil:
        itens_para_exibir = list(set([item.replace("[EQUIPADO] ", "") for item in meus_itens_perfil if item]))
        for item_base in itens_para_exibir:
            col_item_nome, col_item_acao = st.columns([3, 1])
            esta_equipado = f"[EQUIPADO] {item_base}" in meus_itens_perfil
            with col_item_nome:
                if esta_equipado: st.markdown(f"🟢 **{item_base}** *(Equipado)*")
                else: st.markdown(f"⚪ {item_base}")
            with col_item_acao:
                if esta_equipado:
                    if st.button("🔴 Desequipar", key=f"deseq_{item_base}", use_container_width=True):
                        nova_lista = [x for x in meus_itens_perfil if x != f"[EQUIPADO] {item_base}"] + [item_base]
                        supabase.table("perfis_usuarios").update({"itens_exclusivos": nova_lista}).eq("username", user_atual.get('username')).execute()
                        st.rerun()
                else:
                    if st.button("🟢 Equipar", key=f"eq_{item_base}", use_container_width=True):
                        nova_lista = [x for x in meus_itens_perfil if "Moldura" not in x or "Moldura" not in item_base] + [f"[EQUIPADO] {item_base}"]
                        supabase.table("perfis_usuarios").update({"itens_exclusivos": nova_lista}).eq("username", user_atual.get('username')).execute()
                        st.rerun()
    else: st.info("Você não possui itens.")

# --- 7. ABA VISITAR PERFIL ALHEIO ---
elif aba_ativa == "👀 Ver Perfil" and st.session_state.perfil_visitado:
    alvo = st.session_state.perfil_visitado
    try:
        res = supabase.table("perfis_usuarios").select("*").eq("username", alvo).execute()
        if res.data:
            p = res.data[0]
            itens_alvo = p.get('itens_exclusivos', [])
            selo_visitado, moldura_visitado = aplicar_moldura_e_selo(p.get('username'), p.get('titulo', 'Usuário'), itens_alvo, p.get('seguidores', 0))
            
            col_f, col_s = st.columns([1, 2])
            with col_f: 
                f_vis = p.get('foto_perfil')
                if not f_vis or str(f_vis).strip() in ["0", "None", ""] or not str(f_vis).startswith("http"):
                    f_vis = 'https://img.icons8.com/colors/150/test-account.png'
                st.markdown(f'<img src="{f_vis}" style="{moldura_visitado}" width="120">', unsafe_allow_html=True)
            with col_s:
                st.header(f"{p.get('nickname', 'Usuário')}{selo_visitado}")
                st.write(f"@{p.get('username', '')} | {p.get('titulo', 'Usuário')}")
                st.write(f"👥 {p.get('seguidores', 0)} Seguidores")
            st.write(f"📝 {p.get('bio', '')}")
            
            st.write("---")
            c_btn1, c_btn2 = st.columns(2)
            with c_btn1:
                if st.button("👥 Adicionar como Amigo", key="btn_add_amigo_perfil_direto", use_container_width=True):
                    lista_atual_amigos = user_atual.get('lista_amigos', [])
                    if not isinstance(lista_atual_amigos, list): lista_atual_amigos = []
                    if alvo not in lista_atual_amigos:
                        lista_atual_amigos.append(alvo)
                        supabase.table("perfis_usuarios").update({"lista_amigos": lista_atual_amigos}).eq("username", user_atual.get('username')).execute()
                        st.success(f"🎉 @{alvo} adicionado!")
            with c_btn2:
                if st.button("💬 Conversa com Seguidor", key="btn_conversa_direta_perfil", use_container_width=True):
                    st.session_state.sala_privada_atual = obter_id_sala_privada(user_atual.get('username'), alvo)
                    st.session_state.codigo_grupo_atual = None
                    st.success("Sala Privada configurada! Vá até o Chat EXV.")
                
            if st.button("Voltar ao Feed", use_container_width=True):
                st.session_state.perfil_visitado = None
                st.rerun()
    except: st.error("Erro ao carregar perfil.")

# --- 8. PAINEL DEV ---
elif aba_ativa == "⚡ Painel Dev" and user_atual.get('username') == "rafael_oficial":
    st.header("Painel Secreto do Desenvolvedor 👑")
    try:
        usuarios_req = supabase.table("perfis_usuarios").select("username, nickname").execute()
        lista_usuarios = [u["username"] for u in usuarios_req.data]
    except: lista_usuarios = []

    if lista_usuarios:
        usuario_alvo = st.selectbox("Selecione o usuário alvo:", lista_usuarios)
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.subheader("👥 Seguidores")
            qtd_seguidores = st.number_input("Quantidade", min_value=0, value=1000)
            if st.button("Definir", key="btn_seg"):
                supabase.table("perfis_usuarios").update({"seguidores": qtd_seguidores}).eq("username", usuario_alvo).execute()
                st.rerun()
        with col2:
            st.subheader("💰 Coins")
            qtd_dinheiro = st.number_input("Silver Coins", min_value=0, value=500)
            if st.button("Definir", key="btn_money"):
                supabase.table("perfis_usuarios").update({"dinheiro": qtd_dinheiro}).eq("username", usuario_alvo).execute()
                st.rerun()
        with col3:
            st.subheader("🎖️ Cargos")
            novo_titulo = st.selectbox("Cargo:", ["👑 Desenvolvedor", "⚔️ Vice-Dev", "📢 Divulgadora", "🧪 Tester", "🏅 best friends of the dev", "Usuário"])
            if st.button("Atualizar", key="btn_cargo"):
                supabase.table("perfis_usuarios").update({"titulo": novo_titulo}).eq("username", usuario_alvo).execute()
                st.rerun()
        with col4:
            st.subheader("🔨 Moderação")
            st.write("<br>", unsafe_allow_html=True)
            if st.button("🚫 Banir Usuário", key="btn_banir", use_container_width=True):
                supabase.table("perfis_usuarios").update({"titulo": "❌ BANIDO"}).eq("username", usuario_alvo).execute()
                st.rerun()

        # --- SEÇÃO DO GERENCIADOR DE INVENTÁRIO ---
        st.write("---")
        st.subheader("🎒 Gerenciador de Inventário (God Mode)")
        item_para_dar = st.text_input("Nome do Item para dar ao usuário:", placeholder="Ex: 🖼️ Moldura de Fogo 🔥")
        if st.button("🎁 Entregar Item para o Usuário", use_container_width=True):
            if item_para_dar:
                busca_user = supabase.table("perfis_usuarios").select("itens_exclusivos").eq("username", usuario_alvo).execute()
                if busca_user.data:
                    inventario_atual = busca_user.data[0].get('itens_exclusivos', [])
                    if not isinstance(inventario_atual, list): inventario_atual = []
                    inventario_atual.append(item_para_dar)
                    supabase.table("perfis_usuarios").update({"itens_exclusivos": inventario_atual}).eq("username", usuario_alvo).execute()
                    st.success(f"🎉 Item injetado!")
                    st.rerun()

        # --- SEÇÃO DE AÇÕES GLOBAIS ---
        st.write("---")
        st.subheader("⚙️ Ações Globais")
        col_glob1, col_glob2 = st.columns(2)
        with col_glob1:
            valor_bonus = st.number_input("Valor do Bônus Global:", min_value=1, value=100)
            if st.button("💰 Dar Bônus para Todos", use_container_width=True):
                todos = supabase.table("perfis_usuarios").select("username, dinheiro").execute()
                for u in todos.data:
                    novo_saldo = u.get('dinheiro', 0) + valor_bonus
                    supabase.table("perfis_usuarios").update({"dinheiro": novo_saldo}).eq("username", u['username']).execute()
                st.success("Bônus global enviado!")
                st.rerun()
        with col_glob2:
            st.write("<br>", unsafe_allow_html=True)
            if st.button("🧹 APAGAR TODOS OS VÍDEOS", use_container_width=True):
                vids = supabase.table("feed_videos").select("id").execute()
                for v in vids.data: supabase.table("feed_videos").delete().eq("id", v['id']).execute()
                st.rerun()
  
