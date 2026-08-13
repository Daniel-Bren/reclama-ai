import re
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter

CAMINHO_PDF = "data/codigo_defesa_consumidor.pdf"

def criar_chunks(documentos):
    divisor = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )

    chunks = []

    for documento in documentos:
        textos_divididos = divisor.split_text(documento["texto"])

        for indice, texto_chunk in enumerate(textos_divididos):
            chunk = {
                "texto": texto_chunk,
                "metadados": {
                    **documento["metadados"],
                    "chunk": indice
                }
            }

            chunks.append(chunk)

    return chunks


def limpar_texto(texto):
    """
    Remove alguns ruídos comuns da extração do PDF.
    """

    texto = texto.replace("(ÍNDICE)", "")
    texto = texto.replace("", "")

    texto = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", texto)

    texto = re.sub(r"(?m)^\s*\d+\s*$", "", texto)

    texto = re.sub(r"\s*\n\s*", " ", texto)

    texto = re.sub(r"\s+", " ", texto)

    return texto.strip()


def carregar_documento(caminho_pdf):
    leitor = PdfReader(caminho_pdf)

    documentos = []


    for numero_pagina, pagina in enumerate(leitor.pages[5:], start=6):

        texto_original = pagina.extract_text() or ""

        texto_limpo = limpar_texto(texto_original)

        if texto_limpo:
            documento = {
                "texto": texto_limpo,
                "metadados": {
                    "arquivo": "codigo_defesa_consumidor.pdf",
                    "pagina_pdf": numero_pagina,
                    "categoria": "Direito do Consumidor",
                    "fonte": "PROCON-SP",
                    "ano": 2026
                }
            }

            documentos.append(documento)

    return documentos


documentos = carregar_documento(CAMINHO_PDF)

chunks = criar_chunks(documentos)

if __name__ == "__main__":
    documentos = carregar_documento(CAMINHO_PDF)
    chunks = criar_chunks(documentos)

    print(f"Páginas processadas: {len(documentos)}")
    print(f"Chunks criados: {len(chunks)}")

    print("\n--- PRIMEIRO CHUNK ---\n")
    print(chunks[0]["texto"])

    print("\n--- METADADOS ---\n")
    print(chunks[0]["metadados"])