import streamlit as st
from supabase import create_client, Client
import random

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Silver Tok v2", page_icon="🚀", layout="centered")

# --- CONEXÃO COM SUPABASE ---
url = "https://ldjtqgeyorkzbvuichjj.supabase.co"
key = "sb_publishable_ZWY9Hp6kQrhOzff6xc_DrA_8TlnrqQ_"

try:
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error(f"Erro crítico: {str(e)}")
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

CODIGO_CORRETO = "ChatPrivado2026"

TITULOS = {
    "rafael_oficial": "👑 Desenvolvedor",
    "rafael_secundario": "⚔️ Vice-Dev",
    "amiga_divulgadora": "📢 Divulgadora",
}

# --- FUNÇÃO PARA GERAR SELO E MOLDURA DE PERFIL ---
def aplicar_moldura_e_selo(username, titulo, itens_usuario=None, seguidores=0):
    selo = ""
    # Verificação automática de 1000 seguidores para o Verificado
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

# --- FUNÇÕES DE SIMULAÇÃO DO SILVER IA ---
def responder_ia(pergunta):
    respostas_prontas = [
        "Com certeza, Rafael! Como seu assistente Silver, estou aqui para ajudar você a gerenciar o Silver Tok. O que mais quer codar hoje?",
        "Essa é uma excelente pergunta. No ecossistema do Silver Tok v2, eu, Silver, recomendo estruturar isso usando Python e Streamlit.",
        "Analisando os dados da plataforma... Pronto! O Silver encontrou a solução: tente postar vídeos curtos com legendas chamativas para alcançar os 1.000 seguidores mais rápido!",
        "Dica do Silver: O Chat EXV acabou de ser implementado com sucesso. Monitore os servidores para garantir estabilidade.",
        "Olá, eu sou o Silver! Estou processando sua solicitação. Posso te ajudar a criar códigos, responder curiosidades ou planejar novas atualizações."
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
            "username": username,
            "senha": password,
            "nickname": nickname,
            "titulo": titulo,
            "seguidores": 0,
            "seguindo": 0,
            "dinheiro": 0,
            "verificado": False,
            "foto_perfil": "https://img.icons8.com/colors/150/test-account.png",
            "bio": "Olá! Estou usando o Silver Tok.",
            "itens_exclusivos": [],
            "lista_amigos": []
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
                else:
                    st.error("Usuário ou senha incorretos.")
            except Exception as e:
                st.error(f"Erro de conexão com o banco: {str(e)}")
                
    with aba_cadastro:
        new_user = st.text_input("Escolha seu Usuário", key="cad_user").strip()
        new_nick = st.text_input("Nome de Exibição (Nickname)", key="cad_nick")
        new_pass = st.text_input("Escolha sua Senha", type="password", key="cad_pass")
        convite = st.text_input("Código de Convite Secreto", type="password", key="cad_code")
        
        if st.button("Cadastrar Nova Conta", use_container_width=True):
            if not new_user or not new_pass or not new_nick:
                st.warning("Preencha todos os campos!")
            else:
                status = criar_conta(new_user, new_pass, new_nick, convite)
                if status == "Sucesso":
                    st.success("Conta criada! Faça login ao lado.")
                else:
                    st.error(status)
    st.stop()

def atualizar_sessao():
    try:
        res = supabase.table("perfis_usuarios").select("*").eq("username", st.session_state.user_data['username']).execute()
        if res.data:
            st.session_state.user_data = res.data[0]
    except:
        pass

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
    termo = st.text_input("🔍 Pesquisar...", "").strip().lower()
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
                    except: st.error("Não foi possível carregar este vídeo.")
                
                c1, c2, c3 = st.columns(3)
                with c1:
                    if st.button(f"❤️ {v_curtidas}", key=f"l_{v_id}", use_container_width=True):
                        try:
                            supabase.table("feed_videos").update({"curtidas": v_curtidas + 1}).eq("id", v_id).execute()
                            st.rerun()
                        except: pass
                with c2: st.button("🔗 Copiar", key=f"s_{v_id}", use_container_width=True)
                with c3: abrir_comentarios = st.checkbox("💬 Comentários", key=f"tab_c_{v_id}")
                
                if abrir_comentarios:
                    st.write("**@rafael_oficial:** Esse vídeo ficou brabo! 🔥")
                
                if user_atual.get('username') == v_username or user_atual.get('username') == "rafael_oficial":
                    if st.button(f"🗑️ Apagar Vídeo", key=f"d_{v_id}", use_container_width=True):
                        try:
                            supabase.table("feed_videos").delete().eq("id", v_id).execute()
                            st.rerun()
                        except: pass
                st.write("---")

# --- 2. ABA GRAVAR/POSTAR ---
elif aba_ativa == "🎥 Gravar/Postar":
    st.title("🎥 Câmera Silver Tok")
    aba_cam, aba_link = st.tabs(["📸 Gravar com a Câmera", "🔗 Postar por Link"])
    with aba_cam: st.camera_input("Tirar foto/registro para o Feed")
    with aba_link:
        legenda = st.text_input("Legenda do post:")
        url_do_video = st.text_input("Link do vídeo (.mp4):")
        if st.button("Publicar Vídeo", use_container_width=True):
            try:
                supabase.table("feed_videos").insert({
                    "username": user_atual.get('username'), "nickname": user_atual.get('nickname'),
                    "legenda": legenda, "url_video": url_do_video, "curtidas": 0
                }).execute()
                st.success("Publicado no Feed!")
            except Exception as e: st.error(f"Erro ao publicar: {str(e)}")

# --- 3. ABA CHAT EXV ---
elif aba_ativa == "💬 Chat EXV":
    st.title("💬 Chat EXV")
    
    sub_aba_privado, sub_aba_grupo, sub_aba_seguidores, sub_aba_amigos = st.tabs([
        "🔒 Chat Privado", "👥 Chat em Grupo", "📣 Com Seguidores", "🤝 Lista & Add Amigos"
    ])
    
    try:
        todos_users_req = supabase.table("perfis_usuarios").select("username").execute()
        lista_geral_users = [u['username'] for u in todos_users_req.data if u['username'] != user_atual.get('username')]
    except: lista_geral_users = []

    with sub_aba_privado:
        st.subheader("🔒 Conversas Privadas 1x1")
        if lista_geral_users:
            destinatario_p = st.selectbox("Conversar com:", lista_geral_users, key="sel_priv")
            msg_p = st.text_input("Mensagem Privada:", key="txt_priv")
            if st.button("Enviar DM", key="btn_priv"):
                st.success(f"Mensagem enviada de forma privada para @{destinatario_p}!")
        else: st.info("Nenhum outro usuário cadastrado no momento.")

    with sub_aba_grupo:
        st.subheader("👥 Grupos de Conversa Públicos")
        grupo_sel = st.selectbox("Escolha a Sala de Grupo:", ["💬 Geral Resenha", "🎮 Área Gamer", "🚀 Ideias Pró-App"])
        msg_g = st.text_input("Mensagem para o Grupo:", key="txt_grup")
        if st.button("Enviar no Grupo", key="btn_grup"):
            st.info(f"Mensagem enviada no grupo '{grupo_sel}'!")

    with sub_aba_seguidores:
        st.subheader("📣 Conversa com Seguidores")
        msg_seg = st.text_input("Escreva um comunicado/chat para quem te segue:", key="txt_seg")
        if st.button("Transmitir via Chat EXV", key="btn_seg_chat"):
            st.success("Transmitido com sucesso para a sua base de seguidores ativos!")

    with sub_aba_amigos:
        st.subheader("🤝 Gerenciador de Amizades")
        amigo_alvo = st.text_input("Digite o @username exato do seu amigo:", key="add_amigo_input").strip()
        if st.button("➕ Enviar Pedido / Adicionar", use_container_width=True):
            if amigo_alvo == user_atual.get('username'):
                st.error("Você não pode adicionar a si mesmo!")
            elif amigo_alvo in lista_geral_users:
                meus_amigos_atuais = user_atual.get('lista_amigos', [])
                if not isinstance(meus_amigos_atuais, list): meus_amigos_atuais = []
                
                if amigo_alvo not in meus_amigos_atuais:
                    meus_amigos_atuais.append(amigo_alvo)
                    try:
                        supabase.table("perfis_usuarios").update({"lista_amigos": meus_amigos_atuais}).eq("username", user_atual.get('username')).execute()
                        st.success(f"🎉 @{amigo_alvo} agora está na sua Lista de Amigos!")
                        st.rerun()
                    except Exception as e: st.error(f"Erro ao salvar amizade: {str(e)}")
                else: st.warning("Esse usuário já está na sua lista de amigos!")
            else: st.error("Usuário não encontrado no Silver Tok.")
            
        st.write("---")
        st.write("**👥 Minha Lista de Amigos**")
        meus_amigos = user_atual.get('lista_amigos', [])
        if meus_amigos and isinstance(meus_amigos, list):
            for amg in meus_amigos:
                col_a, col_b = st.columns([4, 1])
                col_a.write(f"🤝 **@{amg}**")
                if col_b.button("Remover", key=f"rem_{amg}"):
                    nova_l = [x for x in meus_amigos if x != amg]
                    supabase.table("perfis_usuarios").update({"lista_amigos": nova_l}).eq("username", user_atual.get('username')).execute()
                    st.rerun()
        else: st.info("Sua lista de amigos está vazia no momento.")

# --- 4. ABA SILVER IA ---
elif aba_ativa == "🧠 Silver IA":
    st.title("🧠 Silver IA")
    st.write("Olá! Eu sou o **Silver**, seu assistente oficial do Silver Tok v2. Faça perguntas, peça ideias de posts ou pesquise ferramentas comigo!")
    
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
    st.title("🛒 Loja de Customização")
    st.write(f"💰 **Sua Carteira:** ${user_atual.get('dinheiro', 0)}")
    st.write("---")

    customizacoes = {
        "🖼️ Moldura de Fogo 🔥": 1000,
        "💎 Moldura de Diamante ✨": 2500,
        "🖼️ Banner Estelar (Perfil)": 1500,
        "💬 Caixa de Texto Neon (Feed)": 2000,
        "🌈 Nickname Dourado": 5000
    }

    for item, preco in customizacoes.items():
        with st.container():
            col_info, col_btn = st.columns([3, 1])
            with col_info:
                st.markdown(f"### {item}")
                st.markdown(f"💰 Custo: **${preco}**")
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
                                supabase.table("perfis_usuarios").update({
                                    "dinheiro": novo_saldo, "itens_exclusivos": meus_visuais
                                }).eq("username", user_atual.get('username')).execute()
                                st.success(f"🎉 '{item}' adquirido!")
                                st.rerun()
                            except Exception as e: st.error(f"Erro: {str(e)}")
                        else: st.error("❌ Saldo insuficiente!")
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
        c3.metric("Carteira", f"${user_atual.get('dinheiro', 0)}")
    
    st.write(f"📝 **Bio:** {user_atual.get('bio', 'Disponível')}")
    
    st.write("---")
    st.subheader("👥 Meus Amigos (Visível para Seguidores)")
    lista_amigos_perfil = user_atual.get('lista_amigos', [])
    if lista_amigos_perfil and isinstance(lista_amigos_perfil, list):
        st.write(", ".join([f"@{amg}" for amg in lista_amigos_perfil]))
    else: st.caption("Nenhum amigo adicionado ainda.")
    
    st.write("---")
    st.subheader("🎒 Meu Inventário Visual")
    meus_itens_perfil = [x for x in meus_itens_perfil if x]
    
    if meus_itens_perfil:
        itens_para_exibir = list(set([item.replace("[EQUIPADO] ", "") for item in meus_itens_perfil]))
        for item_base in itens_para_exibir:
            col_item_nome, col_item_acao = st.columns([3, 1])
            esta_equipado = f"[EQUIPADO] {item_base}" in meus_itens_perfil
            
            with col_item_nome:
                if esta_equipado: st.markdown(f"🟢 **{item_base}** *(Equipado)*")
                else: st.markdown(f"⚪ {item_base}")
            
            with col_item_acao:
                if esta_equipado:
                    if st.button("🔴 Desequipar", key=f"deseq_{item_base}", use_container_width=True):
                        nova_lista = [x for x in meus_itens_perfil if x != f"[EQUIPADO] {item_base}"]
                        nova_lista.append(item_base)
                        supabase.table("perfis_usuarios").update({"itens_exclusivos": nova_lista}).eq("username", user_atual.get('username')).execute()
                        st.rerun()
                else:
                    if st.button("🟢 Equipar", key=f"eq_{item_base}", use_container_width=True):
                        nova_lista = []
                        if "Moldura" in item_base:
                            for x in meus_itens_perfil:
                                limpo = x.replace("[EQUIPADO] ", "")
                                if "Moldura" in x:
                                    if limpo not in nova_lista: nova_lista.append(limpo)
                                else:
                                    if x not in nova_lista: nova_lista.append(x)
                        else: nova_lista = list(meus_itens_perfil)
                        
                        if item_base in nova_lista: nova_lista.remove(item_base)
                        nova_lista.append(f"[EQUIPADO] {item_base}")
                        supabase.table("perfis_usuarios").update({"itens_exclusivos": nova_lista}).eq("username", user_atual.get('username')).execute()
                        st.rerun()
    else: st.info("Você não possui itens comprados na loja ainda.")

    st.write("---")
    expander = st.expander("⚙️ Editar Perfil Basic (Mudar Foto e Bio)")
    with expander:
        novo_nick = st.text_input("Mudar Nickname:", value=user_atual.get('nickname', ''))
        nova_bio = st.text_area("Mudar Bio:", value=user_atual.get('bio', ''))
        nova_foto = st.text_input("Link da Foto de Perfil:", value=user_atual.get('foto_perfil', ''))
        if st.button("Salvar Alterações"):
            try:
                supabase.table("perfis_usuarios").update({
                    "nickname": novo_nick, "bio": nova_bio, "foto_perfil": nova_foto
                }).eq("username", user_atual.get('username')).execute()
                st.success("Perfil atualizado!")
                st.rerun()
            except Exception as e: st.error(f"Erro ao salvar: {str(e)}")

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
                if not f_vis or str(f_vis).strip() in ["0", "None", ""]: f_vis = 'https://img.icons8.com/colors/150/test-account.png'
                st.markdown(f'<img src="{f_vis}" style="{moldura_visitado}" width="120">', unsafe_allow_html=True)
            with col_s:
                st.header(f"{p.get('nickname', 'Usuário')}{selo_visitado}")
                st.write(f"@{p.get('username', '')} | {p.get('titulo', 'Usuário')}")
                st.write(f"👥 {p.get('seguidores', 0)} Seguidores")
            
            st.write(f"📝 {p.get('bio', '')}")
            
            st.write("---")
            st.subheader("👥 Lista de Amigos deste Perfil")
            amigos_alvo = p.get('lista_amigos', [])
            if amigos_alvo and isinstance(amigos_alvo, list):
                st.write(", ".join([f"@{a}" for a in amigos_alvo]))
            else: st.caption("Este usuário não tem amigos listados.")
            
            st.write("---")
            if st.button("Voltar ao Feed"):
                st.session_state.perfil_visitado = None
                st.rerun()
    except: st.error("Erro ao carregar o perfil visitado.")

# --- 8. PAINEL DEV (RECUPERADO COMPLETO) ---
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
                try: supabase.table("perfis_usuarios").update({"seguidores": qtd_seguidores}).eq("username", usuario_alvo).execute(); st.rerun()
                except: pass
        with col2:
            st.subheader("💰 Carteira")
            qtd_dinheiro = st.number_input("Dinheiro ($)", min_value=0, value=500)
            if st.button("Definir", key="btn_money"):
                try: supabase.table("perfis_usuarios").update({"dinheiro": qtd_dinheiro}).eq("username", usuario_alvo).execute(); st.rerun()
                except: pass
        with col3:
            st.subheader("🎖️ Cargos")
            novo_titulo = st.selectbox("Cargo:", ["👑 Desenvolvedor", "⚔️ Vice-Dev", "📢 Divulgadora", "🧪 Tester", "🏅 best friends of the dev", "Usuário"])
            if st.button("Atualizar", key="btn_cargo"):
                try: supabase.table("perfis_usuarios").update({"titulo": novo_titulo}).eq("username", usuario_alvo).execute(); st.rerun()
                except: pass
        with col4:
            st.subheader("🔨 Moderação")
            st.write("<br>", unsafe_allow_html=True)
            if st.button("🚫 Banir Usuário", key="btn_banir", use_container_width=True):
                try: supabase.table("perfis_usuarios").update({"titulo": "❌ BANIDO"}).eq("username", usuario_alvo).execute(); st.success(f"@{usuario_alvo} banido!"); st.rerun()
                except Exception as e: st.error(f"Erro: {str(e)}")

        # --- SEÇÃO DO GERENCIADOR DE INVENTÁRIO (RECUPERADO) ---
        st.write("---")
        st.subheader("🎒 Gerenciador de Inventário (God Mode)")
        item_para_dar = st.text_input("Nome do Item para dar ao usuário:", placeholder="Ex: 🖼️ Moldura de Fogo 🔥")
        if st.button("🎁 Entregar Item para o Usuário", use_container_width=True):
            if not item_para_dar: st.warning("Digite o nome de um item antes de enviar!")
            else:
                try:
                    busca_user = supabase.table("perfis_usuarios").select("itens_exclusivos").eq("username", usuario_alvo).execute()
                    if busca_user.data:
                        inventario_atual = busca_user.data[0].get('itens_exclusivos', [])
                        if not isinstance(inventario_atual, list): inventario_atual = []
                        inventario_atual.append(item_para_dar)
                        supabase.table("perfis_usuarios").update({"itens_exclusivos": inventario_atual}).eq("username", usuario_alvo).execute()
                        st.success(f"🎉 '{item_para_dar}' injetado no inventário de @{usuario_alvo}!"); st.rerun()
                except Exception as e: st.error(f"Erro: {str(e)}")

        # --- SEÇÃO DE AÇÕES GLOBAIS (RECUPERADO) ---
        st.write("---")
        st.subheader("⚙️ Ações Globais")
        col_glob1, col_glob2 = st.columns(2)
        with col_glob1:
            valor_bonus = st.number_input("Valor do Bônus Global:", min_value=1, value=100)
            if st.button("💰 Dar Bônus para Todos", use_container_width=True):
                try:
                    todos = supabase.table("perfis_usuarios").select("username, dinheiro").execute()
                    for u in todos.data:
                        novo_saldo = u.get('dinheiro', 0) + valor_bonus
                        supabase.table("perfis_usuarios").update({"dinheiro": novo_saldo}).eq("username", u['username']).execute()
                    st.success("Bônus global enviado!"); st.rerun()
                except: pass
        with col_glob2:
            st.write("<br>", unsafe_allow_html=True)
            if st.button("🧹 APAGAR TODOS OS VÍDEOS", use_container_width=True):
                try:
                    vids = supabase.table("feed_videos").select("id").execute()
                    for v in vids.data: supabase.table("feed_videos").delete().eq("id", v['id']).execute()
                    st.success("Feed limpo!"); st.rerun()
                except: pass
