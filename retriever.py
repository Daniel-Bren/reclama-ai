from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings


from vector_store import MODELO_EMBEDDING, PASTA_BANCO

def carregar_banco_vetorial():
    embedding = HuggingFaceEmbeddings(
        model_name=MODELO_EMBEDDING
    )

    banco = FAISS.load_local(
        PASTA_BANCO,
        embedding,
        allow_dangerous_deserialization=True
    )
    return banco

def buscar_documentos(pergunta, quantidade=6):
    banco = carregar_banco_vetorial()

    documentos = banco.similarity_search(
        pergunta,
        k=quantidade
    )

    return documentos

if __name__ == "__main__":
    pergunta = "Comprei um produto que apresentou defeito. O que posso fazer?"

    resultados = buscar_documentos(pergunta)

    print(f"\nPERGUNTA: {pergunta}")

    for indice, documento in enumerate(resultados, start=1):
        print(f"\n---RESULTADO {indice}---\n")
        print(documento.page_content)

        print("\nMetadados:")
        print(documento.metadata)
