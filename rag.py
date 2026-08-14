from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

from retriever import buscar_documentos

load_dotenv()

MODELO_LLM = "gemini-3.6-flash"

def montar_contexto(documentos):
    partes = []

    for indice, documento in enumerate(documentos, start=1):
        metadata = documento.metadata

        fonte = (
            f"[FONTE {indice}] "
            f"Arquivo: {metadata.get('arquivo', 'desconhecido')} | "
            f"Página: {metadata.get('pagina_pdf', 'desconhecida')} | "
            f"Artigo: {metadata.get('artigo', 'não identificado')}"
        )

        partes.append(
            f"{fonte}\n{documento.page_content}"
        )

    return "\n\n".join(partes)

def responder(pergunta):
    documentos = buscar_documentos(pergunta)

    contexto = montar_contexto(documentos)

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
Você é o RECLAMA AI, um assistente informativo sobre direitos do consumidor.

Responda exclusivamente com base no CONTEXTO fornecido.

Regras:
- Não utilize conhecimento externo ao contexto.
- Não invente artigos, prazos, direitos ou obrigações.
- Sempre cite a fonte utilizada no formato:
  [arquivo, página X].
- Não cite apenas "FONTE 1", "FONTE 2" etc.
- Utilize exatamente o nome do arquivo e a página informados no contexto.
- Se o contexto não contiver informação suficiente para responder,
  diga claramente:
  "Não encontrei essa informação nos documentos disponíveis."
- Explique a resposta em linguagem simples e acessível.
- Quando possível, mencione o artigo relacionado.
- Não se apresente como advogado.
- A resposta tem caráter informativo e não substitui orientação jurídica profissional.
"""

        ),
        (
            "human",
            """
PERGUNTA:
{pergunta}

CONTEXTO:
{contexto}
"""
        )
    ])

    modelo = ChatGoogleGenerativeAI(
        model=MODELO_LLM,
        max_retries=2
    )

    chain = prompt | modelo

    MENSAGEM_FALLBACK = "Não encontrei essa informação nos documentos disponíveis."

    resposta = chain.invoke({
        "pergunta": pergunta,
        "contexto": contexto
    })

    texto_resposta = resposta.text.strip()

    if texto_resposta.startswith(MENSAGEM_FALLBACK):
        return texto_resposta, []

    return texto_resposta, documentos


if __name__ == "__main__":
    pergunta = "Comprei um produto que apresentou defeito. O que posso fazer?"

    resposta, fontes = responder(pergunta)

    print("\n--- RESPOSTA DO RECLAMA AI ---\n")
    print(resposta)

    print("\n--- FONTES RECUPERADAS ---\n")

    if fontes:
        for fonte in fontes:
            print({
                "arquivo": fonte.metadata.get("arquivo"),
                "pagina": fonte.metadata.get("pagina_pdf"),
                "artigo": fonte.metadata.get("artigo")
            })
    else:
        print("Nenhuma fonte relevante encontrada.")