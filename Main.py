import streamlit as st
from supabase import create_client, Client
import random
import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st. set_page_config ( page_title= "Silver Tok v2" , page_icon= "🚀" , layout= "centered" )

# --- CONEXÃO COM SUPABASE ---
url = "https://ldjtqgeyorkzbvuichjj.supabase.co"
chave = "sb_publishable_ZWY9Hp6kQrhOzff6xc_DrA_8TlnrqQ_"

try:
    supabase: client = create_client ( url, chave )
except Exception as e:
    st.error ( f"Erro crítico de conexão: { str ( e ) } " )
# st.stop()

# --- ESTADO DE DESENVOLVIMENTO ---
ESTADO_DESENVOLVIMENTO = True 

# --- INICIALIZAÇÃO DA SESSÃO ---
if "logado" not in st.session_state :
    st. session_state . logado = False
if "user_data" not in st. session_state :
    st. session_state . user_data = None
if "perfil_visitado"not in st. session_state :
    st. session_state . perfil_visitado = None
if "historico_ia" not in st. session_state :
    st. session_state . historico_ia = [ ]

# --- BANCO DE DADOS LOCAL DO CHAT E LIVES (Sessão Ativa) ---
if "chat_privado_salas" not in st. session_state :
    st. session_state . chat_privado_salas = {  } 
if "chat_grupos" not in st. session_state :
    st. session_state . chat_grupos = {  } 
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

# --- 5. ABA LOJA DO SITE ---
elif aba_ativa == "🛒 Loja do Site":
    st.title("🛒 Loja de Customizações")
    # Usa a tua carteira real do teu sistema original
    st.write(f"🪙 **Carteira:** {user_atual.get('dinheiro', 0)} Silver Coins")
    st.write("---")

    # [NOVO] Puxar os itens dinâmicos ativos direto do teu banco de dados
    try:
        resposta = supabase.table("loja_itens").select("*").eq("ativo", True).execute()
        itens_banco = resposta.data if hasattr(resposta, 'data') else resposta.get('data', [])
    except Exception as e:
        st.error("Erro ao carregar os itens da loja.")
        itens_banco = []

    # Se o banco estiver vazio, mostra o aviso
    if not itens_banco:
        st.info("A loja está a ser reabastecida pelo administrador. Volta em breve! 🌟")
    else:
        # Loop para mostrar cada item cadastrado por ti no banco
        for item in itens_banco:
            nome_produto = item["nome_produto"]
            preco = int(item["preco"])
            descricao = item.get("descricao", "Sem descrição disponível.")
            imagem_url = item.get("imagem_url", "")

            with st.container():
                # Criamos 3 colunas para incluir a imagem do produto lindamente
                col_img, col_info, col_btn = st.columns([1, 2, 1])
                
                with col_img:
                    if imagem_url and str(imagem_url).startswith("http"):
                        st.image(imagem_url, use_container_width=True)
                    else:
                        st.subheader("🖼️") # Se não tiver foto, mostra o emoji padrão
                
                with col_info: 
                    st.markdown(f"### {nome_produto}\n*{descricao}*\n\n🪙 Custo: **{preco} Coins**")
                
                with col_btn:
                    st.write("<br>", unsafe_allow_html=True)
                    
                    # Carrega o teu sistema de inventário original seguro
                    meus_visuais = user_atual.get('itens_exclusivos', [])
                    if not isinstance(meus_visuais, list): meus_visuais = []
                    meus_visuais = [x for x in meus_visuais if x]
                    
                    # Verifica se o utilizador já comprou o item do banco
                    if nome_produto in meus_visuais or f"[EQUIPADO] {nome_produto}" in meus_visuais:
                        st.button("✅ Adquirido", key=f"loja_{item['id']}", disabled=True, use_container_width=True)
                    else:
                        if st.button(f"🛒 Adquirir", key=f"comprar_{item['id']}", use_container_width=True):
                            saldo = user_atual.get('dinheiro', 0)
                            if saldo >= preco:
                                try:
                                    meus_visuais.append(nome_produto)
                                    # Atualiza exatamente a tua tabela original 'perfis_usuarios'
                                    supabase.table("perfis_usuarios").update({
                                        "dinheiro": saldo - preco, 
                                        "itens_exclusivos": meus_visuais
                                    }).eq("username", user_atual.get('username')).execute()
                                    
                                    st.success(f"🎉 Adquirido!")
                                    st.balloons()
                                    st.rerun()
                                except Exception as e: 
                                    st.error(f"Erro: {str(e)}")
                            else: 
                                st.error("❌ Saldo insuficiente!")
            st.write("---")
     # --- 6. ABA MEU PERFIL (SINCRONIZADO COM SUPABASE) ---
elif aba_ativa == "👤 Meu Perfil":
     # ==========================================================
    # --- NOVO BLOCO 3: BANCO DE DADOS DE ITENS FIXOS (20 DE CADA) ---
    # ========================================================== 
    # 🎫 1. CÁTALOGO DE MOLDURAS (20 Itens)
    catalogo_molduras = {
        "Moldura angelical": "https://cdn.jsdelivr.net/gh/rafael1202lessa-bot/tesio@main/moldura-anjo.png",
        "Moldura Cyberpunk": "https://cdn.jsdelivr.net/gh/rafael1202lessa-bot/tesio@main/moldura_cyber.png",
        "Moldura de Cavaleiro": "",
        "Moldura de Dragão Branco": "",
    }
    # Preenche automaticamente do 4 ao 20 para o seu catálogo ficar pronto
    for i in range(4, 21):
        catalogo_molduras[f"Moldura {i}"] = ""  # É só colar o link correspondente aqui quando tiver!

    # 🗺️ 2. ESTILOS DE BANNERS DINÂMICOS (20 Cores/Estilos Diferentes)
    estilos_banners = {
        "Padrão": "linear-gradient(135deg, #6a11cb 0%, #2575fc 100%)",
        "Banner de Cavaleiro": "linear-gradient(135deg, #2c3e50 0%, #0f2027 100%)",
        "Banner de Dragão Branco": "linear-gradient(135deg, #e0e0e0 0%, #ffffff 50%, #b0c4de 100%)",
        "Banner 4 (Fogo)": "linear-gradient(135deg, #f12711 0%, #f5af19 100%)",
        "Banner 5 (Neon)": "linear-gradient(135deg, #00f260 0%, #0575e6 100%)",
        "Banner 6 (Sombrio)": "linear-gradient(135deg, #111111 0%, #434343 100%)",
        "Banner 7 (Vampiro)": "linear-gradient(135deg, #4e0000 0%, #000000 100%)",
        "Banner 8 (Oceano)": "linear-gradient(135deg, #2b5876 0%, #4e4376 100%)",
        "Banner 9 (Rosa Choque)": "linear-gradient(135deg, #f857a6 0%, #ff5858 100%)",
        "Banner 10 (Esmeralda)": "linear-gradient(135deg, #11998e 0%, #38ef7d 100%)",
        "Banner 11 (Ouro Imperial)": "linear-gradient(135deg, #bf953f 0%, #fcf6ba 50%, #b38728 100%)",
        "Banner 12 (Roxo Galáxia)": "linear-gradient(135deg, #3f2b96 0%, #a8c0ff 100%)",
        "Banner 13 (Tóxico)": "linear-gradient(135deg, #111 0%, #a8ff78 100%)",
        "Banner 14 (Gelo)": "linear-gradient(135deg, #eef2f3 0%, #8e9eab 100%)",
        "Banner 15 (Magma)": "linear-gradient(135deg, #ff9900 0%, #ff5500 100%)",
        "Banner 16 (Ametista)": "linear-gradient(135deg, #6441a5 0%, #2a0845 100%)",
        "Banner 17 (Cavalaria Real)": "linear-gradient(135deg, #130cb7 0%, #52e5e7 100%)",
        "Banner 18 (Sakura)": "linear-gradient(135deg, #ffc3a0 0%, #ffafbd 100%)",
        "Banner 19 (Cyber Rosa)": "linear-gradient(135deg, #ee0979 0%, #ff6a00 100%)",
        "Banner 20 (Divino)": "linear-gradient(135deg, #fff7ad 0%, #ffa9f9 100%)"
    }

    # 🏷️ 3. CONFIGURAÇÕES DAS 20 CAIXAS DE NOME
    estilos_caixas_nome = {
        "Normal": "color: #ffffff;",
        "Caixa Cavaleiresca": "background: #1a1c23; border: 3px solid; border-image: linear-gradient(135deg, #d4af37, #e5e5e5) 1;",
        "Caixa 3": "background: #000; border: 2px dashed #00ff00; color: #00ff00;",
        "Caixa 4": "background: linear-gradient(45deg, #f12711, #f5af19); border-radius: 12px;",
        "Caixa 5": "background: #000000; border: 2px solid #ff007f; box-shadow: 0 0 10px #ff007f;",
    }
    for i in range(6, 21):
        estilos_caixas_nome[f"Caixa Nome {i}"] = f"background: #222; border-left: 5px solid hsl({i*18}, 70%, 50%);"

    # 💬 4. CONFIGURAÇÕES DAS 20 CAIXAS DE MENSAGENS (BALÕES DE CHAT)
    estilos_caixas_mensagem = {
        "Normal": "background: #262730; color: #fff;",
        "Mensagem 1": "background: rgba(255, 215, 0, 0.1); border: 1px solid #ffd700;",
        "Mensagem 2": "background: rgba(0, 242, 96, 0.1); border-left: 4px solid #00f260;",
        "Mensagem 3": "background: #111111; border: 1px solid #ff0055; color: #ff0055;"
    }
    for i in range(4, 21):
        estilos_caixas_mensagem[f"Mensagem {i}"] = f"background: #1a1a1a; border-bottom: 2px solid hsl({i*15}, 60%, 50%);"


    # ==========================================================
    # --- PROCESSO DE CHECAGEM DOS ITENS EQUIPADOS ---
    # ==========================================================
    link_moldura = None
    nome_moldura_ativa = ""
    banner_background = estilos_banners["Padrão"]
    estilo_nome_ativo = estilos_caixas_nome["Normal"]
    estilo_msg_ativo = estilos_caixas_mensagem["Normal"]
    
    caixa_nome_equipada = False
    caixa_nome_custom_css = ""

    # Garante segurança da lista de itens
    if 'meus_itens_perfil' not in locals() or meus_itens_perfil is None:
        meus_itens_perfil = user_atual.get('itens_exclusivos', [])
    if not isinstance(meus_itens_perfil, list):
        meus_itens_perfil = []

    for item in meus_itens_perfil:
        if "[EQUIPADO]" in item:
            nome_limpo = item.replace("[EQUIPADO] ", "")
            
            # Varre Molduras
            if "Moldura" in nome_limpo:
                nome_moldura_ativa = nome_limpo
                link_moldura = catalogo_molduras.get(nome_limpo)
            
            # Varre Banners
            if nome_limpo in estilos_banners:
                banner_background = estilos_banners[nome_limpo]
            elif "Banner" in nome_limpo: # Fallback automático por número
                banner_background = estilos_banners.get(nome_limpo, estilos_banners["Padrão"])

            # Varre Caixas de Nome
            if nome_limpo == "Caixa Cavaleiresca":
                caixa_nome_equipada = True
            elif nome_limpo in estilos_caixas_nome or "Caixa Nome" in nome_limpo:
                caixa_nome_custom_css = estilos_caixas_nome.get(nome_limpo, estilos_caixas_nome["Normal"])

            # Varre Caixas de Mensagem
            if nome_limpo in estilos_caixas_mensagem or "Mensagem" in nome_limpo:
                estilo_msg_ativo = estilos_caixas_mensagem.get(nome_limpo, estilos_caixas_mensagem["Normal"])

    # Ajuste automático do Banner baseado na moldura clássica caso o usuário não tenha banner comprado separado
    if banner_background == estilos_banners["Padrão"]:
        if nome_moldura_ativa == "Moldura de Cavaleiro":
            banner_background = estilos_banners["Banner de Cavaleiro"]
        elif nome_moldura_ativa == "Moldura de Dragão Branco":
            banner_background = estilos_banners["Banner de Dragão Branco"]

    # Tratamento seguro da foto
    if not foto_url or str(foto_url).strip() in ["0", "None", ""]: 
        foto_url = "https://img.icons8.com/colors/150/test-account.png"


    # ==========================================================
    # --- RENDERIZAÇÃO DO BANNER ---
    # ==========================================================
    st.markdown(f'''
        <div style="position: relative; width: 100%; height: 180px; background: {banner_background}; border-radius: 15px; margin-bottom: 50px; overflow: visible; box-shadow: 0px 4px 15px rgba(0,0,0,0.2);">
            
            <!-- ⚔️ SE FOR TEMA CAVALEIRO, MOSTRA O BRASÃO NO BANNER -->
            {'''<div style="position: absolute; right: 40px; top: 50%; transform: translateY(-50%); width: 90px; height: 110px; background: linear-gradient(135deg, #e0e0e0 0%, #b8b8b8 100%); border: 4px solid #7f8c8d; border-radius: 10px 10px 45px 45px; display: flex; align-items: center; justify-content: center; z-index:1;"><div style="position: absolute; width: 45px; height: 45px; background: #f1c40f; border-radius: 50%;"></div><div style="position: absolute; width: 6px; height: 85px; background: #ecf0f1; transform: rotate(45deg);"></div></div>''' if nome_moldura_ativa == "Moldura de Cavaleiro" else ""}
            
            <!-- 🐉 SE FOR TEMA DRAGÃO, ADICIONA AS ASAS POR TRÁS -->
            {'''<div style="position: absolute; top: -15px; left: -25px; width: 150px; height: 60px; z-index: 0; display: flex; justify-content: space-between;"><div style="width: 45px; height: 45px; background: #fff; border: 2px solid #b0c4de; border-radius: 0 100% 0 100%; transform: rotate(-15deg);"></div><div style="width: 45px; height: 45px; background: #fff; border: 2px solid #b0c4de; border-radius: 100% 0 100% 0; transform: rotate(15deg);"></div></div>''' if nome_moldura_ativa == "Moldura de Dragão Branco" else ""}

            <!-- 👤 RECIPIENTE DA FOTO + MOLDURA CENTRALIZADA NO MEIO -->
            <div style="position: absolute; bottom: -40px; left: 20px; width: 100px; height: 100px;">
                <img src="{foto_url}" style="width: 100px; height: 100px; border-radius: 50%; object-fit: cover; position: absolute; top: 0; left: 0; border: 4px solid #fff; box-shadow: 0px 4px 10px rgba(0,0,0,0.2); z-index: 1;">
                {"".join(f'<img src="{link_moldura}" style="width: 155px; height: 155px; object-fit: contain; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); pointer-events: none; z-index: 2;">' if link_moldura else "")}
            </div>
        </div>
    ''', unsafe_allow_html=True)


    # ==========================================================
    # --- RENDERIZAÇÃO DA CAIXA DE NOME ---
    # ==========================================================
    selo_meu_perfil, _ = aplicar_moldura_e_selo(user_atual.get('username'), user_atual.get('titulo'), meus_itens_perfil, user_atual.get('seguidores', 0))
    nickname_usuario = user_atual.get('nickname', 'Usuário')

    if caixa_nome_equipada:
        # Mantém o design premium da caixa cavaleiresca que você pediu
        st.markdown(f'''
            <div style="position: relative; margin-top: 15px; margin-bottom: 15px; padding: 15px 30px; background: #1a1c23; border: 3px solid; border-image: linear-gradient(135deg, #d4af37, #e5e5e5, #aa7c11, #b4b4b4) 1; border-radius: 8px; box-shadow: 0px 4px 15px rgba(0,0,0,0.4); display: inline-block; min-width: 250px; overflow: hidden;">
                <div style="position: absolute; top: 50%; left: 5%; transform: translateY(-50%) rotate(25deg); width: 90%; height: 4px; background: rgba(200,200,200,0.15); z-index: 1;"><div style="position: absolute; left: 0; top: -4px; width: 12px; height: 12px; background: #aa7c11; border-radius: 50%;"></div></div>
                <div style="position: absolute; top: 50%; left: 5%; transform: translateY(-50%) rotate(-25deg); width: 90%; height: 4px; background: rgba(200,200,200,0.15); z-index: 1;"><div style="position: absolute; right: 0; top: -4px; width: 12px; height: 12px; background: #aa7c11; border-radius: 50%;"></div></div>
                <div style="position: relative; z-index: 2; font-size: 26px; font-weight: bold; color: #ffffff; display: flex; align-items: center; gap: 10px;">
                    <span>{nickname_usuario}</span> <span style="font-size: 20px;">{selo_meu_perfil}</span>
                </div>
            </div>
        ''', unsafe_allow_html=True)
    elif caixa_nome_custom_css:
        # Renderiza dinamicamente qualquer uma das outras caixas de nome de 3 a 20
        st.markdown(f'<div style="padding: 10px 20px; display: inline-block; font-size: 24px; font-weight: bold; {caixa_nome_custom_css}">{nickname_usuario} {selo_meu_perfil}</div>', unsafe_allow_html=True)
    else:
        st.header(f"{nickname_usuario}{selo_meu_perfil}")
        
    st.caption(f"🆔 **@{user_atual.get('username', '')}** | Cargo: *{user_atual.get('titulo', 'Usuário')}*")
                                                            
    # ==========================================================
    # --- RENDERIZAÇÃO DO BANNER PREMIUM ---
    # ==========================================================
              # HTML definitivo com centralização absoluta automática no meio
    if link_moldura:
        st.markdown(f'<div style="position: relative; width: 100%; height: 180px; background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%); border-radius: 15px; margin-bottom: 50px;"><div style="position: absolute; bottom: -40px; left: 20px; width: 100px; height: 100px;"><img src="{foto_url}" style="width: 100px; height: 100px; border-radius: 50%; object-fit: cover; position: absolute; top: 0; left: 0; border: 4px solid #fff; box-shadow: 0px 4px 10px rgba(0,0,0,0.2); z-index: 1;"><img src="{link_moldura}" style="width: 155px; height: 155px; object-fit: contain; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); pointer-events: none; z-index: 2;"></div></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="position: relative; width: 100%; height: 180px; background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%); border-radius: 15px; margin-bottom: 50px;"><img src="{foto_url}" style="position: absolute; bottom: -40px; left: 20px; width: 100px; height: 100px; border-radius: 50%; border: 4px solid #fff; object-fit: cover; box-shadow: 0px 4px 10px rgba(0,0,0,0.2);"></div>', unsafe_allow_html=True)

    # 3. STATUS DO USUÁRIO
    selo_meu_perfil, _ = aplicar_moldura_e_selo(user_atual.get('username'), user_atual.get('titulo'), meus_itens_perfil, user_atual.get('seguidores', 0))
    st.header(f"{user_atual.get('nickname', 'Usuário')}{selo_meu_perfil}")
    st.caption(f"🆔 **@{user_atual.get('username', '')}** | Cargo: *{user_atual.get('titulo', 'Usuário')}*")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Seguidores", f"👥 {user_atual.get('seguidores', 0)}")
    m2.metric("Seguindo", f"🏃 {user_atual.get('seguindo', 0)}")
    m3.metric("Saldo", f"🪙 {user_atual.get('dinheiro', 0)}")
    st.write("---")
    
    # 4. ABAS INTERNAS
    sub_aba_perfil, sub_aba_inventario, sub_aba_editar, sub_aba_convites, sub_aba_seguidores = st.tabs(["📋 Meus Dados", "🎒 Meu Inventário", "⚙️ Editar Perfil", "✉️ Convites", "👥 Amigos"])
    
    with sub_aba_perfil:
        st.subheader("📋 Informações da Conta")
        st.markdown(f"**Bio atual:** {user_atual.get('bio', '*Nenhuma biografia adicionada.*')}")

    # 5. INVENTÁRIO ATUALIZADO EM TEMPO REAL
    with sub_aba_inventario:
        if meus_itens_perfil:
            # Exibe os itens sem repetir e sem a tag de equipado no nome
            itens_exib = list(set([i.replace("[EQUIPADO] ", "") for i in meus_itens_perfil if i]))
            for it in itens_exib:
                col_n, col_a = st.columns([3, 1])
                eq = f"[EQUIPADO] {it}" in meus_itens_perfil
                with col_n: 
                    st.markdown(f"🟢 **{it} (Equipado)**" if eq else f"⚪ {it}")
                with col_a:
                    if eq:
                        if st.button("Desequipar", key=f"d_{it}", use_container_width=True):
                            # Monta a nova lista sem o marcador de equipado
                            nl = [x for x in meus_itens_perfil if x != f"[EQUIPADO] {it}"]
                            if it not in nl: 
                                nl.append(it)
                            # Salva direto no Supabase e limpa o cache da sessão
                            supabase.table("perfis_usuarios").update({"itens_exclusivos": nl}).eq("username", user_atual.get('username')).execute()
                            if 'meus_itens_perfil' in st.session_state:
                                del st.session_state['meus_itens_perfil']
                            st.rerun()
                    else:
                        if st.button("Equipar", key=f"e_{it}", use_container_width=True):
                            nl = []
                            # Se equipar moldura, desequipa as outras molduras antes
                            for x in meus_itens_perfil:
                                if "Moldura" in it and "Moldura" in x and "[EQUIPADO]" in x:
                                    nl.append(x.replace("[EQUIPADO] ", ""))
                                else:
                                    nl.append(x)
                            if it in nl: 
                                nl.remove(it)
                            nl.append(f"[EQUIPADO] {it}")
                            # Salva direto no Supabase e limpa o cache da sessão
                            supabase.table("perfis_usuarios").update({"itens_exclusivos": nl}).eq("username", user_atual.get('username')).execute()
                            if 'meus_itens_perfil' in st.session_state:
                                del st.session_state['meus_itens_perfil']
                            st.rerun()
        else:
            st.info("Inventário vazio.")
                
    with sub_aba_editar:
        n_nick = st.text_input("Nickname:", value=user_atual.get('nickname'))
        n_foto = st.text_input("URL Foto:", value=user_atual.get('foto_perfil'))
        n_bio = st.text_area("Bio:", value=user_atual.get('bio'), max_chars=150)
        if st.button("💾 Salvar Perfil", use_container_width=True):
            supabase.table("perfis_usuarios").update({"nickname": n_nick, "foto_perfil": n_foto, "bio": n_bio}).eq("username", user_atual.get('username')).execute()
            st.success("Salvo!")
            st.rerun()

    with sub_aba_convites:
        st.subheader("✉️ Sistema de Convites Compartilhados")
        if user_atual.get('username') == "rafael_oficial":
            st.info("👑 **Vantagem de Desenvolvedor:** Seus convites são **INFINITOS** e ilimitados!")
        else:
            st.metric("Seus Créditos de Convite Restantes:", f"🎫 {user_atual.get('convites_restantes', 0)} de 3")
        
        link_gerado = f"https://silvertokv2.streamlit.app/?ref={user_atual.get('username')}"
        st.markdown("### 🔗 Seu Link de Convite Exclusivo:")
        st.code(link_gerado, language="text")
        st.caption("Envie esse link para seus amigos. Ao entrarem por ele, o sistema pula o código secreto automaticamente!")

    with sub_aba_seguidores:
        amg_add = st.text_input("Seguir usuário (@):").strip()
        if st.button("➕ Seguir") and amg_add:
            chk = supabase.table("perfis_usuarios").select("username").eq("username", amg_add).execute()
            if chk.data:
                la = user_atual.get('lista_amigos', [])
                if not isinstance(la, list): la = []
                if amg_add not in la:
                    la.append(amg_add)
                    supabase.table("perfis_usuarios").update({"lista_amigos": la, "seguindo": user_atual.get('seguindo', 0) + 1}).eq("username", user_atual.get('username')).execute()
                    st.success("Seguindo!")
                    st.rerun()
              
# --- 7. ABA VISITAR PERFIL ALHEIO ---
if aba_ativa == "👀 Ver Perfil" and st.session_state.perfil_visited:
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
      # Mantenha o botão de apagar acima e cole este bloco exatamente com estes espaços na frente:
    st.write("---")
    st.subheader("🆕 Cadastrar Novo Item na Loja")
    
    nome_produto = st.text_input("Nome do Produto:", placeholder="Ex: Conta VIP Silver Tok", key="prod_nome_dev")
    preco_produto = st.number_input("Preço do Item (sc):", min_value=0.0, value=5.0, step=1.0, key="prod_preco_dev")
    imagem_produto = st.text_input("Link da Imagem/Ícone:", placeholder="https://...", key="prod_img_dev")
    desc_produto = st.text_area("Descrição/Benefícios do Produto:", placeholder="O que o usuário ganha...", key="prod_desc_dev")
    
    if st.button("🚀 Publicar na Loja Oficial", use_container_width=True, key="btn_loja_dev"):
        if nome_produto.strip() and preco_produto > 0:
            try:
                supabase.table("loja_itens").insert({
                    "nome_produto": nome_produto.strip(),
                    "preco": preco_produto,
                    "imagem_url": imagem_produto.strip(),
                    "descricao": desc_produto.strip()
                }).execute()
                st.success(f"🎉 Item '{nome_produto}' adicionado com sucesso à loja!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar no banco: {str(e)}")
        else:
            st.warning("Por favor, preencha o nome do produto e defina um preço válido.")
        # GERENCIADOR DE REMOVER/ATIVAR PRODUTOS VIA BANCO DE DADOS
    st.write("---")
    st.subheader("📦 Gerenciar Itens da Loja")

    try:
        resposta_dev = supabase.table("loja_itens").select("*").execute()
        todos_itens = resposta_dev.data if hasattr(resposta_dev, 'data') else resposta_dev.get('data', [])
    except Exception as e:
        todos_itens = []

    if not todos_itens:
        st.info("Nenhum produto cadastrado no banco de dados.")
    else:
        for item in todos_itens:
            # Pega o status ativo (se for None, assume True por segurança)
            esta_ativo = item.get("ativo", True)
            status_texto = "🟢 Ativo na Loja" if esta_ativo else "🔴 Ocultado/Removido"
            
            # Garante que vai ler 'nome_produto' ou apenas 'nome' dependendo do banco
            nome_item = item.get("nome_produto") or item.get("nome") or "Item Sem Nome"
            moeda_item = item.get("moeda", "SC") # Puxa se é R$ ou SC
            
            with st.container():
                col_nome, col_status, col_btn = st.columns([2, 1, 1])
                with col_nome:
                    st.markdown(f"**{nome_item}**\n\n💰 {item.get('preco')} {moeda_item}")
                with col_status:
                    st.write(f"Status:\n{status_texto}")
                with col_btn:
                    st.write("<br>", unsafe_allow_html=True)
                    
                    # ID do item para usar como chave única no banco e no Streamlit
                    id_item = item.get("id")
                    
                    if esta_ativo:
                        if st.button("Remover", key=f"dev_rem_{id_item}", use_container_width=True):
                            try:
                                supabase.table("loja_itens").update({"ativo": False}).eq("id", id_item).execute()
                                st.success("Item removido com sucesso!")
                                st.rerun()
                            except Exception as erro: 
                                st.error(f"Erro: {erro}")
                    else:
                        if st.button("Ativar", key=f"dev_atv_{id_item}", use_container_width=True):
                            try:
                                supabase.table("loja_itens").update({"ativo": True}).eq("id", id_item).execute()
                                st.success("Item reativado com sucesso!")
                                st.rerun()
                            except Exception as erro: 
                                st.error(f"Erro: {erro}")
            
            st.write("---")
    
