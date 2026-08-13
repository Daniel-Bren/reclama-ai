from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

from document_loader import carregar_documento, criar_chunks, CAMINHO_PDF

MODELO_EMBEDDING = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
PASTA_BANCO = "faiss_index"

def criar_banco_vetorial():
    documentos = carregar_documento(CAMINHO_PDF)
    chunks = criar_chunks(documentos)

    documentos_langchain = []

    for chunk in chunks:
        documento = Document(
            page_content=chunk["texto"],
            metadata=chunk["metadados"],
        )

        documentos_langchain.append(documento)

    embeddings = HuggingFaceEmbeddings(
        model_name=MODELO_EMBEDDING
    )

    banco_vetorial = FAISS.from_documents(
        documentos_langchain,
        embeddings
    )

    banco_vetorial.save_local(PASTA_BANCO)

    return banco_vetorial

if __name__ == "__main__":
    banco = criar_banco_vetorial()

    print("Banco vetorial criado com sucesso")