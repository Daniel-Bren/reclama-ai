import html
import re
from datetime import datetime
import json
import time

import streamlit as st

from rag import responder


APP_NAME = "RECLAMA AI"
ASSISTANT_INTRO = (
    "Olá! Sou o RECLAMA AI, um agente de IA informativo sobre direitos do "
    "consumidor. Conte o que aconteceu e eu consultarei os documentos "
    "disponíveis para responder com fontes."
)


def criar_mensagem_inicial():
    return {
        "role": "assistant",
        "content": ASSISTANT_INTRO,
        "sources": [],
        "created_at": datetime.now().strftime("%H:%M"),
    }


def inicializar_estado():
    if "mensagens" not in st.session_state:
        st.session_state.mensagens = [criar_mensagem_inicial()]

    if "feedbacks" not in st.session_state:
        st.session_state.feedbacks = {}


def nova_conversa():
    st.session_state.mensagens = [criar_mensagem_inicial()]
    st.session_state.feedbacks = {}
    st.session_state.pop("pergunta_pendente", None)


def montar_historico(limite=8):
    mensagens = st.session_state.get("mensagens", [])
    linhas = []

    for mensagem in mensagens[-limite:]:
        conteudo = mensagem.get("content", "")
        if not conteudo:
            continue

        if mensagem.get("role") == "user":
            autor = "Usuário"
        elif mensagem.get("role") == "assistant":
            autor = APP_NAME
        else:
            continue

        linhas.append(f"{autor}: {conteudo}")

    return "\n".join(linhas) if linhas else "Nenhuma conversa anterior."


def extrair_fontes_citadas(resposta, documentos):
    padrao = (
        r"\[([^,\]]+),\s*página\s*(\d+)"
        r"(?:,\s*Art\.?\s*([^\]]+))?\]"
    )
    citacoes = re.findall(padrao, resposta, flags=re.IGNORECASE)

    fontes = []
    adicionadas = set()

    for arquivo, pagina, artigo_citado in citacoes:
        pagina = int(pagina)
        chave = (arquivo.strip(), pagina)

        if chave in adicionadas:
            continue

        fonte = {
            "arquivo": arquivo.strip(),
            "pagina": pagina,
            "artigo": artigo_citado.strip() or None,
        }

        for documento in documentos or []:
            metadata = getattr(documento, "metadata", {})
            if (
                metadata.get("arquivo") == fonte["arquivo"]
                and metadata.get("pagina_pdf") == pagina
            ):
                fonte["artigo"] = metadata.get("artigo")
                break

        fontes.append(fonte)
        adicionadas.add(chave)

    return fontes


def registrar_pergunta(pergunta):
    pergunta = pergunta.strip()
    if not pergunta:
        return

    historico = montar_historico()
    st.session_state.mensagens.append(
        {
            "role": "user",
            "content": pergunta,
            "sources": [],
            "created_at": datetime.now().strftime("%H:%M"),
        }
    )

    st.session_state.pergunta_pendente = {
        "pergunta": pergunta,
        "historico": historico,
    }

def registrar_execucao(pergunta, resposta, documentos, tempo_resposta):
    registro = {
        "timestamp": datetime.now().isoformat(),
        "pergunta": pergunta,
        "resposta": resposta,
        "fontes": [
            {
                "arquivo": doc.metadata.get("arquivo"),
                "pagina": doc.metadata.get("pagina_pdf"),
                "artigo": doc.metadata.get("artigo"),
            }
            for doc in documentos or []
        ],
        "tempo_resposta_segundos": round(tempo_resposta, 2),
    }
    print(json.dumps(registro, ensure_ascii=False))

def responder_pergunta_pendente():
    pendente = st.session_state.get("pergunta_pendente")
    if not pendente:
        return

    inicio = time.perf_counter()

    with st.spinner("Consultando os documentos..."):
        resposta, documentos = responder(
            pendente["pergunta"],
            historico=pendente["historico"],
        )

    tempo_resposta = time.perf_counter() - inicio

    registrar_execucao(
        pergunta=pendente["pergunta"],
        resposta=resposta,
        documentos=documentos,
        tempo_resposta=tempo_resposta,
    )
    st.session_state.mensagens.append(
        {
            "role": "assistant",
            "content": resposta,
            "sources": extrair_fontes_citadas(resposta, documentos),
            "created_at": datetime.now().strftime("%H:%M"),
        }
    )
    del st.session_state.pergunta_pendente


def aplicar_css():
    st.markdown(
        """
        <style>
        :root {
            color-scheme: light;
            --green-900: #063d2e;
            --green-800: #07543e;
            --green-700: #087a55;
            --green-600: #0b8f63;
            --green-100: #dff3e8;
            --green-50: #eff8f3;
            --ink: #17211e;
            --gray-700: #45534e;
            --gray-600: #5f6e69;
            --gray-500: #78857f;
            --gray-300: #cbd5d1;
            --gray-200: #dce4e1;
            --gray-100: #eef2f0;
            --canvas: #f4f7f6;
            --white: #ffffff;
        }

        html, body, [data-testid="stAppViewContainer"], .stApp {
            background: var(--canvas) !important;
            color: var(--ink) !important;
        }

        .stApp {
            --primary-color: var(--green-700);
            --background-color: var(--canvas);
            --secondary-background-color: var(--gray-100);
            --text-color: var(--ink);
        }

        .stApp p,
        .stApp li,
        .stApp label,
        .stApp input,
        .stApp textarea {
            color: var(--ink);
        }

        [data-testid="stHeader"] {
            background: transparent !important;
            height: 0 !important;
            min-height: 0 !important;
        }

        [data-testid="stDecoration"],
        [data-testid="stStatusWidget"],
        #MainMenu,
        footer {
            display: none !important;
        }

        [data-testid="stToolbar"] {
            display: flex !important;
            position: fixed !important;
            top: .75rem !important;
            left: .75rem !important;
            width: auto !important;
            height: auto !important;
            z-index: 1000 !important;
        }

        [data-testid="stToolbar"] > div {
            width: auto !important;
        }

        [data-testid="stAppDeployButton"],
        [data-testid="stToolbarActions"] {
            display: none !important;
        }

        [data-testid="stExpandSidebarButton"] {
            display: flex !important;
            width: 2.25rem !important;
            height: 2.25rem !important;
            min-height: 2.25rem !important;
            background: var(--white) !important;
            border: 1px solid var(--gray-200) !important;
            border-radius: 7px !important;
            color: var(--green-800) !important;
            box-shadow: 0 4px 14px rgba(23, 33, 30, .10) !important;
        }

        [data-testid="stExpandSidebarButton"] [data-testid="stIconMaterial"],
        [data-testid="stSidebarCollapseButton"] [data-testid="stIconMaterial"] {
            color: var(--green-800) !important;
        }

        [data-testid="stSidebarCollapseButton"] button {
            background: var(--white) !important;
            border: 1px solid var(--gray-200) !important;
            color: var(--green-800) !important;
        }

        [data-testid="stSidebarCollapsedControl"] {
            position: fixed !important;
            top: .75rem !important;
            left: .75rem !important;
            z-index: 1000 !important;
            visibility: visible !important;
        }

        [data-testid="stSidebarCollapsedControl"] button {
            background: var(--white) !important;
            border: 1px solid var(--gray-200) !important;
            color: var(--green-800) !important;
            box-shadow: 0 4px 14px rgba(23, 33, 30, .10);
        }

        [data-testid="stMainBlockContainer"] {
            max-width: 940px !important;
            padding: 1rem 1rem 10rem !important;
        }

        [data-testid="stSidebar"] {
            background: var(--white) !important;
            border-right: 1px solid var(--gray-200);
        }

        [data-testid="stSidebar"] > div:first-child {
            padding-top: 1.25rem;
        }

        [data-testid="stSidebar"] hr {
            border-color: var(--gray-200);
        }

        .sidebar-brand {
            display: flex;
            align-items: center;
            gap: .7rem;
            color: var(--green-900);
            font-size: 1.05rem;
            font-weight: 800;
            margin: 0 0 1rem;
        }

        .sidebar-brand-mark {
            width: 34px;
            height: 34px;
            display: grid;
            place-items: center;
            border-radius: 6px;
            background: var(--green-700);
            color: var(--white);
            font-size: .8rem;
        }

        .sidebar-title {
            color: var(--gray-600);
            font-size: .76rem;
            font-weight: 700;
            margin: 1.15rem 0 .55rem;
            text-transform: uppercase;
        }

        .history-item {
            background: var(--gray-100);
            border-left: 3px solid var(--green-600);
            border-radius: 0 6px 6px 0;
            color: var(--gray-700);
            font-size: .86rem;
            line-height: 1.35;
            margin-bottom: .45rem;
            padding: .58rem .7rem;
        }

        .history-empty,
        .sidebar-note {
            color: var(--gray-600);
            font-size: .82rem;
            line-height: 1.45;
        }

        .product-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            background: var(--green-800);
            border-radius: 8px;
            color: var(--white);
            padding: 1.1rem 1.25rem;
            box-shadow: 0 8px 24px rgba(6, 61, 46, .16);
        }

        .brand-lockup {
            display: flex;
            align-items: center;
            gap: .85rem;
            min-width: 0;
        }

        .brand-mark {
            width: 44px;
            height: 44px;
            flex: 0 0 44px;
            display: grid;
            place-items: center;
            border-radius: 7px;
            background: var(--white);
            color: var(--green-800);
            font-size: .9rem;
            font-weight: 900;
        }

        .brand-name {
            color: var(--white) !important;
            font-size: 1.55rem;
            font-weight: 850;
            line-height: 1.1;
        }

        .brand-tagline {
            color: rgba(255, 255, 255, .82) !important;
            font-size: .88rem;
            margin-top: .25rem;
        }

        .ai-badge {
            display: inline-flex;
            align-items: center;
            gap: .45rem;
            flex: 0 0 auto;
            border: 1px solid rgba(255, 255, 255, .35);
            border-radius: 999px;
            color: var(--white);
            font-size: .78rem;
            font-weight: 700;
            padding: .42rem .7rem;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #79e3ad;
        }

        .conversation-title {
            padding-top: .55rem;
        }

        .conversation-title strong {
            display: block;
            color: var(--green-900);
            font-size: 1.05rem;
        }

        .conversation-title span {
            color: var(--gray-600);
            font-size: .84rem;
        }

        [data-testid="stHorizontalBlock"]:has(.conversation-title) {
            align-items: center;
            margin: .35rem 0 .45rem;
        }

        .ai-disclosure {
            background: var(--green-50);
            border: 1px solid #c7e7d5;
            border-left: 4px solid var(--green-600);
            border-radius: 7px;
            color: var(--gray-700);
            font-size: .88rem;
            line-height: 1.45;
            margin: .2rem 0 1rem;
            padding: .68rem .85rem;
        }

        .ai-disclosure strong {
            color: var(--green-900);
        }

        [data-testid="stChatMessage"] {
            width: fit-content;
            min-width: 250px;
            max-width: 86%;
            align-items: flex-start;
            gap: .65rem;
            background: var(--white) !important;
            border: 1px solid var(--gray-200);
            border-radius: 8px;
            box-shadow: 0 4px 14px rgba(23, 33, 30, .055);
            margin: .7rem auto .7rem 0;
            padding: .8rem .9rem;
        }

        [data-testid="stChatMessage"]:has([aria-label="Chat message from user"]) {
            flex-direction: row-reverse;
            background: var(--green-100) !important;
            border-color: #bcdcca;
            margin-left: auto;
            margin-right: 0;
            max-width: 74%;
        }

        [data-testid="stChatMessage"] > div:first-child {
            width: 2.1rem !important;
            height: 2.1rem !important;
            flex: 0 0 2.1rem !important;
            display: grid !important;
            place-items: center !important;
            border: 1px solid var(--gray-200);
            border-radius: 50% !important;
            background: var(--green-50) !important;
            color: var(--green-800) !important;
            box-shadow: none !important;
        }

        [data-testid="stChatMessage"]:has([aria-label="Chat message from user"])
        > div:first-child {
            background: var(--white) !important;
        }

        [data-testid="stChatMessageContent"] {
            min-width: 0;
            color: var(--ink) !important;
        }

        [data-testid="stChatMessageContent"] p,
        [data-testid="stChatMessageContent"] li,
        [data-testid="stChatMessageContent"] strong,
        [data-testid="stChatMessageContent"] em {
            color: var(--ink) !important;
            line-height: 1.55;
        }

        [data-testid="stChatMessageContent"] a {
            color: var(--green-700) !important;
        }

        [data-testid="stChatMessageContent"] p:last-child {
            margin-bottom: 0;
        }

        .message-meta {
            color: var(--gray-600);
            font-size: .75rem;
            font-weight: 600;
            margin: 0 0 .32rem;
        }

        [data-testid="stChatMessage"]:has([aria-label="Chat message from user"])
        .message-meta {
            text-align: right;
        }

        .source-details {
            border-top: 1px solid var(--gray-200);
            margin-top: .7rem;
            padding-top: .55rem;
        }

        .source-details summary {
            display: flex;
            align-items: center;
            justify-content: space-between;
            color: var(--green-800);
            cursor: pointer;
            font-size: .82rem;
            font-weight: 750;
            list-style: none;
        }

        .source-details summary::-webkit-details-marker {
            display: none;
        }

        .source-details summary::after {
            content: "+";
            color: var(--green-700);
            font-size: 1rem;
            font-weight: 500;
        }

        .source-details[open] summary::after {
            content: "−";
        }

        .source-list {
            display: grid;
            gap: .4rem;
            margin-top: .55rem;
        }

        .source-item {
            background: var(--gray-100);
            border-radius: 5px;
            color: var(--gray-700);
            font-size: .8rem;
            line-height: 1.35;
            padding: .52rem .62rem;
        }

        .source-empty {
            border-top: 1px solid var(--gray-200);
            color: var(--gray-600);
            font-size: .78rem;
            margin-top: .7rem;
            padding-top: .55rem;
        }

        .feedback-label {
            color: var(--gray-600);
            font-size: .78rem;
            padding-top: .35rem;
        }

        [data-testid="stChatMessage"] [data-testid="stHorizontalBlock"] {
            align-items: center;
            gap: .35rem;
            margin-top: .25rem;
        }

        [data-testid="stChatMessage"] .stButton > button {
            min-height: 2rem;
            height: 2rem;
            padding: .15rem .4rem;
        }

        .stButton > button {
            background: var(--white) !important;
            border: 1px solid var(--gray-300) !important;
            border-radius: 7px;
            color: var(--green-800) !important;
            font-weight: 700;
            box-shadow: none;
        }

        .stButton > button p {
            color: inherit !important;
        }

        .stButton > button:hover {
            background: var(--green-50);
            border-color: var(--green-600);
            color: var(--green-900) !important;
        }

        .stButton > button[kind="primary"] {
            background: var(--green-700) !important;
            border-color: var(--green-700) !important;
            color: var(--white) !important;
        }

        [data-testid="stBaseButton-secondary"] {
            background: var(--white) !important;
            border-color: var(--gray-300) !important;
            color: var(--green-800) !important;
        }

        .stButton > button[kind="primary"]:hover {
            background: var(--green-800);
            border-color: var(--green-800);
        }

        [data-testid="stBottomBlockContainer"] {
            background: var(--canvas) !important;
            border-top: 1px solid var(--gray-200);
            padding: .75rem 1rem 1rem !important;
        }

        div:has(> [data-testid="stBottomBlockContainer"]) {
            background: var(--canvas) !important;
        }

        [data-testid="stBottomBlockContainer"] > div {
            max-width: 940px !important;
            margin: 0 auto !important;
        }

        [data-testid="stChatInput"] {
            min-height: 56px;
            background: var(--white) !important;
            border: 1px solid var(--gray-300) !important;
            border-radius: 8px !important;
            box-shadow: 0 6px 20px rgba(23, 33, 30, .09) !important;
        }

        [data-testid="stChatInput"] > div:first-child {
            background: var(--white) !important;
            border: 1px solid var(--gray-300) !important;
            border-radius: 8px !important;
        }

        [data-testid="stChatInput"]:focus-within > div:first-child {
            border-color: var(--green-600) !important;
            box-shadow: 0 0 0 1px var(--green-600) !important;
        }

        [data-testid="stChatInput"] textarea {
            background: transparent !important;
            color: var(--ink) !important;
            caret-color: var(--green-700);
        }

        [data-testid="stChatInput"] textarea::placeholder {
            color: var(--gray-500) !important;
            opacity: 1;
        }

        [data-testid="stChatInputSubmitButton"] {
            color: var(--green-700) !important;
        }

        @media (max-width: 780px) {
            [data-testid="stMainBlockContainer"] {
                padding: 3.75rem .7rem 9rem !important;
            }

            .product-header {
                align-items: flex-start;
                padding: .9rem;
            }

            .brand-name {
                font-size: 1.3rem;
            }

            .brand-tagline {
                font-size: .8rem;
            }

            .ai-badge {
                padding: .35rem .5rem;
            }

            [data-testid="stChatMessage"],
            [data-testid="stChatMessage"]:has([aria-label="Chat message from user"]) {
                min-width: 0;
                max-width: 94%;
            }

            [data-testid="stBottomBlockContainer"] {
                padding: .55rem .65rem .75rem !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def renderizar_topo():
    st.markdown(
        """
        <header class="product-header">
            <div class="brand-lockup">
                <div class="brand-mark">RA</div>
                <div>
                    <div class="brand-name">RECLAMA AI</div>
                    <div class="brand-tagline">Direitos do consumidor com fontes claras</div>
                </div>
            </div>
            <div class="ai-badge">
                <span class="status-dot"></span>
                Agente de IA
            </div>
        </header>
        """,
        unsafe_allow_html=True,
    )

    col_titulo, col_acao = st.columns([4, 1.45])
    with col_titulo:
        st.markdown(
            """
            <div class="conversation-title">
                <strong>Conversa atual</strong>
                <span>Descreva o problema com suas próprias palavras.</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_acao:
        if st.button(
            "＋ Nova conversa",
            key="nova_conversa_topo",
            use_container_width=True,
            help="Apagar as mensagens desta sessão e começar novamente",
        ):
            nova_conversa()
            st.rerun()


def renderizar_sidebar():
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand">
                <span class="sidebar-brand-mark">RA</span>
                RECLAMA AI
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "＋ Nova conversa",
            key="nova_conversa_sidebar",
            use_container_width=True,
            type="primary",
        ):
            nova_conversa()
            st.rerun()

        st.markdown(
            '<div class="sidebar-title">Histórico desta sessão</div>',
            unsafe_allow_html=True,
        )

        mensagens_usuario = [
            mensagem
            for mensagem in st.session_state.mensagens
            if mensagem.get("role") == "user"
        ]

        if not mensagens_usuario:
            st.markdown(
                '<div class="history-empty">Suas perguntas aparecerão aqui.</div>',
                unsafe_allow_html=True,
            )
        else:
            for indice, mensagem in enumerate(mensagens_usuario, start=1):
                texto = mensagem.get("content", "").strip()
                resumo = texto[:74] + ("..." if len(texto) > 74 else "")
                st.markdown(
                    f'<div class="history-item"><strong>{indice}.</strong> '
                    f"{html.escape(resumo)}</div>",
                    unsafe_allow_html=True,
                )

        st.divider()
        st.markdown(
            """
            <div class="sidebar-note">
                Conteúdo informativo. Não substitui atendimento jurídico,
                órgãos de defesa do consumidor ou análise profissional.
            </div>
            """,
            unsafe_allow_html=True,
        )


def renderizar_fontes(fontes):
    if not fontes:
        st.markdown(
            """
            <div class="source-empty">
                Nenhuma fonte documental foi identificada nesta resposta.
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    itens = []
    for fonte in fontes:
        arquivo = html.escape(str(fonte.get("arquivo", "Documento")))
        pagina = html.escape(str(fonte.get("pagina", "-")))
        artigo = fonte.get("artigo")
        artigo_texto = ""
        if artigo and artigo != "contexto":
            artigo = html.escape(str(artigo))
            prefixo = "" if artigo.lower().startswith("art") else "Art. "
            artigo_texto = f" · {prefixo}{artigo}"

        itens.append(
            '<div class="source-item">'
            f"<strong>{arquivo}</strong> · página {pagina}{artigo_texto}"
            "</div>"
        )

    quantidade = len(fontes)
    rotulo = "Fonte consultada" if quantidade == 1 else "Fontes consultadas"
    st.markdown(
        f"""
        <details class="source-details">
            <summary>{rotulo} ({quantidade})</summary>
            <div class="source-list">{''.join(itens)}</div>
        </details>
        """,
        unsafe_allow_html=True,
    )


def registrar_feedback(indice, valor):
    st.session_state.feedbacks[indice] = valor


def renderizar_feedback(indice):
    feedback_atual = st.session_state.feedbacks.get(indice)
    col_info, col_pos, col_neg = st.columns([7, 1, 1])

    with col_info:
        if feedback_atual == "positivo":
            texto = "Obrigado. Resposta marcada como útil."
        elif feedback_atual == "negativo":
            texto = "Obrigado. Feedback registrado."
        else:
            texto = "Esta resposta ajudou?"

        st.markdown(
            f'<div class="feedback-label">{texto}</div>',
            unsafe_allow_html=True,
        )

    with col_pos:
        st.button(
            "👍",
            key=f"positivo_{indice}",
            help="Marcar resposta como útil",
            on_click=registrar_feedback,
            args=(indice, "positivo"),
            use_container_width=True,
        )

    with col_neg:
        st.button(
            "👎",
            key=f"negativo_{indice}",
            help="Marcar resposta como pouco útil",
            on_click=registrar_feedback,
            args=(indice, "negativo"),
            use_container_width=True,
        )


def renderizar_chat():
    st.markdown(
        """
        <div class="ai-disclosure">
            <strong>Você está conversando com uma inteligência artificial.</strong>
            As respostas são informativas e baseadas nos documentos do projeto.
        </div>
        """,
        unsafe_allow_html=True,
    )

    for indice, mensagem in enumerate(st.session_state.mensagens):
        role = mensagem.get("role", "assistant")
        avatar = "⚖️" if role == "assistant" else "👤"

        with st.chat_message(role, avatar=avatar):
            autor = "Agente de IA" if role == "assistant" else "Você"
            horario = html.escape(mensagem.get("created_at", ""))
            st.markdown(
                f'<div class="message-meta">{autor} · {horario}</div>',
                unsafe_allow_html=True,
            )
            st.markdown(mensagem.get("content", ""))

            if role == "assistant" and indice > 0:
                renderizar_fontes(mensagem.get("sources", []))
                renderizar_feedback(indice)


def main():
    st.set_page_config(
        page_title=APP_NAME,
        page_icon="⚖️",
        layout="wide",
        initial_sidebar_state="auto",
    )

    inicializar_estado()
    aplicar_css()
    renderizar_sidebar()
    renderizar_topo()
    renderizar_chat()

    pergunta = st.chat_input(
        "Digite sua dúvida sobre consumo"
    )

    if pergunta:
        registrar_pergunta(pergunta)
        st.rerun()

    if st.session_state.get("pergunta_pendente"):
        responder_pergunta_pendente()
        st.rerun()


if __name__ == "__main__":
    main()
