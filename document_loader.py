import re
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter

CAMINHO_PDF = "data/codigo_defesa_consumidor.pdf"

def criar_chunks(documentos):
    """
    Divide o documento priorizando a estrutura jurídica por artigos.
    Artigos muito grandes ainda são subdivididos.
    """

    divisor_artigo_longo = RecursiveCharacterTextSplitter(
        chunk_size=1600,
        chunk_overlap=200,
        length_function=len
    )

    chunks = []
    contador_chunk = 0

    # Procura inícios como:
    # Art. 2º
    # Art. 18.
    # Art. 54-A
    padrao_artigo = r"(?=Art\.\s*\d+(?:-[A-Z])?[º°]?)"

    for documento in documentos:
        texto = documento["texto"]

        partes = re.split(padrao_artigo, texto)

        for parte in partes:
            parte = parte.strip()

            if not parte:
                continue

            # Descobre qual artigo existe nesse trecho, se houver
            artigo_encontrado = re.match(
                r"Art\.\s*(\d+(?:-[A-Z])?[º°]?)",
                parte
            )

            if artigo_encontrado:
                numero_artigo = artigo_encontrado.group(1)
            else:
                numero_artigo = "contexto"

            # Artigos muito grandes ainda podem precisar ser divididos
            if len(parte) > 1600:
                subpartes = divisor_artigo_longo.split_text(parte)
            else:
                subpartes = [parte]

            for indice_parte, texto_chunk in enumerate(subpartes):
                chunk = {
                    "texto": texto_chunk,
                    "metadados": {
                        **documento["metadados"],
                        "artigo": numero_artigo,
                        "parte_artigo": indice_parte,
                        "chunk": contador_chunk
                    }
                }

                chunks.append(chunk)
                contador_chunk += 1

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