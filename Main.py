import streamlit as st
from supabase import create_client, Client

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

CODIGO_CORRETO = "ChatPrivado2026"

TITULOS = {
    "rafael_oficial": "👑 Desenvolvedor",
    "rafael_secundario": "⚔️ Vice-Dev",
    "amiga_divulgadora": "📢 Divulgadora",
}

# --- FUNÇÃO PARA GERAR SELO E MOLDURA DE PERFIL ---
def aplicar_moldura_e_selo(username, titulo, moldura_ativa=None):
    selo = ""
    if username == "rafael_oficial":
        selo = " ✨[👑 DEV]"
    elif "Dev" in str(titulo) or "Desenvolvedor" in str(titulo):
        selo = " 🛠️[DEV]"
    elif titulo == "🏅 best friends of the dev":
        selo = " 🌟"
        
    # Estilo CSS padrão da imagem redonda
    estilo_moldura = "border-radius: 50%; object-fit: cover;"
    
    # Aplica a borda apenas se a moldura estiver ATIVA no perfil
    if moldura_ativa == "🖼️ Moldura de Fogo 🔥":
        estilo_moldura = "border-radius: 50%; object-fit: cover; border: 4px solid #FF4500; box-shadow: 0 0 15px #FF8C00;"
    elif moldura_ativa == "💎 Moldura de Diamante ✨":
        estilo_moldura = "border-radius: 50%; object-fit: cover; border: 4px solid #00FFFF; box-shadow: 0 0 15px #00BFFF;"
            
    return selo, estilo_moldura

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
            "moldura_ativa": None,
            "banner_ativo": None,
            "caixa_ativa": None
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

# Validações globais de banimento e manutenção
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

# Pega a moldura ativa atual do usuário
moldura_corrente = user_atual.get('moldura_ativa')
selo_sidebar, estilo_da_moldura = aplicar_moldura_e_selo(user_atual.get('username', ''), user_atual.get('titulo', ''), moldura_corrente)

st.sidebar.markdown(f'<img src="{foto_side}" style="{estilo_da_moldura}" width="100">', unsafe_allow_html=True)
st.sidebar.write("") 

st.sidebar.title(f"@{user_atual.get('username', '')}{selo_sidebar}")
if st.sidebar.button("Sair da Conta"):
    st.session_state.logado = False
    st.rerun()


# --- MENU PRINCIPAL ---
abas = ["📱 Feed", "🎥 Gravar/Postar", "🛒 Loja do Site", "👤 Meu Perfil"]
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
    except:
        videos = []

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
                m_ativa_autor = None
                try:
                    autor_req = supabase.table("perfis_usuarios").select("*").eq("username", v_username).execute()
                    if autor_req.data:
                        foto_autor = autor_req.data[0].get('foto_perfil', foto_autor)
                        if not foto_autor or str(foto_autor).strip() in ["0", "None", ""]:
                            foto_autor = "https://img.icons8.com/colors/150/test-account.png"
                        titulo_autor = autor_req.data[0].get('titulo', 'Usuário')
                        m_ativa_autor = autor_req.data[0].get('moldura_ativa')
                except:
                    pass
                
                selo_post, moldura_post = aplicar_moldura_e_selo(v_username, titulo_autor, m_ativa_autor)
                
                col_foto, col_nome = st.columns([1, 5])
                with col_foto:
                    st.markdown(f'<img src="{foto_autor}" style="{moldura_post}" width="50">', unsafe_allow_html=True)
                with col_nome:
                    if st.button(f"**{v_nickname}** (@{v_username}){selo_post}", key=f"u_{v_id}"):
                        st.session_state.perfil_visitado = v_username
                        st.rerun()
                
                if v_legenda: st.write(v_legenda)
                
                if v_url:
                    try:
                        st.video(v_url)
                    except:
                        st.error("Não foi possível carregar este vídeo.")
                
                c1, c2, c3 = st.columns(3)
                with c1:
                    if st.button(f"❤️ {v_curtidas}", key=f"l_{v_id}", use_container_width=True):
                        try:
                            supabase.table("feed_videos").update({"curtidas": v_curtidas + 1}).eq("id", v_id).execute()
                            st.rerun()
                        except:
                            pass
                with c2:
                    st.button("🔗 Copiar", key=f"s_{v_id}", use_container_width=True)
                with c3:
                    abrir_comentarios = st.checkbox("💬 Comentários", key=f"tab_c_{v_id}")
                
                if abrir_comentarios:
                    st.write("**@rafael_oficial:** Esse vídeo ficou brabo! 🔥")
                
                if user_atual.get('username') == v_username or user_atual.get('username') == "rafael_oficial":
                    if st.button(f"🗑️ Apagar Vídeo", key=f"d_{v_id}", use_container_width=True):
                        try:
                            supabase.table("feed_videos").delete().eq("id", v_id).execute()
                            st.rerun()
                        except:
                            pass
                st.write("---")

# --- 2. ABA GRAVAR/POSTAR ---
elif aba_ativa == "🎥 Gravar/Postar":
    st.title("🎥 Câmera Silver Tok")
    aba_cam, aba_link = st.tabs(["📸 Gravar com a Câmera", "🔗 Postar por Link"])
    
    with aba_cam:
        st.camera_input("Tirar foto/registro para o Feed")
            
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
            except Exception as e:
                st.error(f"Erro ao publicar: {str(e)}")

# --- 3. ABA LOJA DO SITE ---
elif aba_ativa == "🛒 Loja do Site":
    st.title("🛒 Loja de Customização")
    st.write(f"💰 **Sua Carteira:** ${user_atual.get('dinheiro', 0)}")
    st.write("Compre itens visuais para mudar a cara do seu perfil!")
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
                if not isinstance(meus_visuais, list):
                    meus_visuais = []
                
                if item in meus_visuais:
                    st.button("✅ Adquirido", key=f"loja_{item}", disabled=True, use_container_width=True)
                else:
                    if st.button(f"🛒 Adquirir", key=f"comprar_{item}", use_container_width=True):
                        saldo = user_atual.get('dinheiro', 0)
                        if saldo >= preco:
                            try:
                                novo_saldo = saldo - preco
                                meus_visuais.append(item)
                                supabase.table("perfis_usuarios").update({
                                    "dinheiro": novo_saldo,
                                    "itens_exclusivos": meus_visuais
                                }).eq("username", user_atual.get('username')).execute()
                                st.success(f"🎉 '{item}' adquirido!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro: {str(e)}")
                        else:
                            st.error("❌ Saldo insuficiente!")
            st.write("---")

# --- 4. ABA MEU PERFIL (SISTEMA DE EQUIPAR/DESEQUIPAR ATIVADO!) ---
elif aba_ativa == "👤 Meu Perfil":
    meus_itens_perfil = user_atual.get('itens_exclusivos', [])
    m_ativa = user_atual.get('moldura_ativa')
    
    selo_meu_perfil, moldura_meu_perfil = aplicar_moldura_e_selo(user_atual.get('username'), user_atual.get('titulo'), m_ativa)
    
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
    
    # --- GERENCIADOR DE INVENTÁRIO (EQUIPAR / DESEQUIPAR CORES E MOLDURAS) ---
    st.write("---")
    st.subheader("🎒 Meu Inventário Visual")
    
    if meus_itens_perfil:
        for item in meus_itens_perfil:
            col_item_nome, col_item_acao = st.columns([3, 1])
            with col_item_nome:
                st.markdown(f"✨ **{item}**")
            
            with col_item_acao:
                # Lógica para MOLDURAS
                if "Moldura" in item:
                    if m_ativa == item:
                        if st.button("🔴 Desequipar", key=f"deseq_{item}", use_container_width=True):
                            supabase.table("perfis_usuarios").update({"moldura_active": None, "moldura_ativa": None}).eq("username", user_atual.get('username')).execute()
                            st.rerun()
                    else:
                        if st.button("🟢 Equipar", key=f"eq_{item}", use_container_width=True):
                            supabase.table("perfis_usuarios").update({"moldura_ativa": item}).eq("username", user_atual.get('username')).execute()
                            st.rerun()
                else:
                    # Outros itens estéticos (Banners / Caixas) por enquanto mostram como Ativos
                    st.caption("Ativado")
    else:
        st.info("Você não possui itens comprados na loja ainda.")

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
            except Exception as e:
                st.error(f"Erro ao salvar: {str(e)}")

    st.write("---")
    st.subheader("🎬 Meus Vídeos")
    try:
        meus_vids = supabase.table("feed_videos").select("*").eq("username", user_atual.get('username')).execute()
        for v in meus_vids.data: 
            if v.get('url_video'): st.video(v['url_video'])
    except:
        st.info("Nenhum vídeo publicado.")

# --- 5. ABA VISITAR PERFIL ALHEIO ---
elif aba_ativa == "👀 Ver Perfil" and st.session_state.perfil_visitado:
    alvo = st.session_state.perfil_visitado
    try:
        res = supabase.table("perfis_usuarios").select("*").eq("username", alvo).execute()
        if res.data:
            p = res.data[0]
            m_alvo = p.get('moldura_ativa')
            selo_visitado, moldura_visitado = aplicar_moldura_e_selo(p.get('username'), p.get('titulo', 'Usuário'), m_alvo)
            
            col_f, col_s = st.columns([1, 2])
            with col_f: 
                f_vis = p.get('foto_perfil')
                if not f_vis or str(f_vis).strip() in ["0", "None", ""]:
                    f_vis = 'https://img.icons8.com/colors/150/test-account.png'
                st.markdown(f'<img src="{f_vis}" style="{moldura_visitado}" width="120">', unsafe_allow_html=True)
            with col_s:
                st.header(f"{p.get('nickname', 'Usuário')}{selo_visitado}")
                st.write(f"@{p.get('username', '')} | {p.get('titulo', 'Usuário')}")
                st.write(f"👥 {p.get('seguidores', 0)} Seguidores")
            
            st.write(f"📝 {p.get('bio', '')}")
            st.write("---")
            if st.button("Voltar ao Feed"):
                st.session_state.perfil_visitado = None
                st.rerun()
            
            vids = supabase.table("feed_videos").select("*").eq("username", alvo).execute()
            for v in vids.data: 
                if v.get('url_video'): st.video(v['url_video'])
    except:
        st.error("Erro ao carregar o perfil visitado.")

# --- 6. PAINEL DEV ---
elif aba_ativa == "⚡ Painel Dev" and user_atual.get('username') == "rafael_oficial":
    st.header("Painel Secreto do Desenvolvedor 👑")
    try:
        usuarios_req = supabase.table("perfis_usuarios").select("username, nickname").execute()
        lista_usuarios = [u["username"] for u in usuarios_req.data]
    except:
        lista_usuarios = []

    if lista_usuarios:
        usuario_alvo = st.selectbox("Selecione o usuário alvo:", lista_usuarios)
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.subheader("👥 Seguidores")
            qtd_seguidores = st.number_input("Quantidade", min_value=0, value=1000)
            if st.button("Definir", key="btn_seg"):
                try: supabase.table("perfis_usuarios").update({"seguidores": qtd_seguidores, "verificado": qtd_seguidores >= 1000}).eq("username", usuario_alvo).execute(); st.rerun()
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

        # --- SEÇÃO DO GERENCIADOR DE INVENTÁRIO ---
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

        # --- SEÇÃO DE AÇÕES GLOBAIS ---
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
