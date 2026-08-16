RECLAMA AI

Agente de Inteligência Artificial para consulta de direitos do consumidor.

Projeto desenvolvido como parte do Alura Agent do programa Oracle ONE Next Generation 2026.

O projeto:
Um agente de IA criado para responder dúvidas sobre direitos do consumidor com base em documentos oficiais.
O sistema utiliza uma arquitetura RAG — Retrieval-Augmented Generation, combinando busca semântica em documentos com um modelo de linguagem.

A proposta é permitir que o usuário faça perguntas em linguagem natural.

O agente busca os trechos mais relevantes da legislação, envia esse contexto ao modelo de linguagem e gera uma resposta simples, citando as fontes utilizadas.

* O RECLAMA AI possui caráter informativo e não substitui orientação jurídica profissional.

Problema:
A legislação de defesa do consumidor contém muitas informações importantes, mas nem sempre é fácil para o usuário localizar o artigo ou interpretar o texto jurídico.
O RECLAMA AI busca reduzir essa dificuldade oferecendo uma interface conversacional capaz de consultar os documentos e explicar o conteúdo em linguagem mais acessível.

Solução:
O projeto utiliza IA generativa combinada com recuperação semântica de documentos.

Pergunta do usuário -> Busca semântica -> FAISS -> Trechos relevantes do CDC -> Prompt com contexto -> Gemini -> Resposta com fontes

Arquitetura:

O RECLAMA AI utiliza uma arquitetura RAG:
Pergunta do usuário → busca semântica → FAISS → trechos relevantes do CDC → Gemini → resposta com fontes.

Principais componentes:
- `document_loader.py`: leitura, limpeza e divisão do documento.
- `vector_store.py`: geração dos embeddings e criação do índice FAISS.
- `retriever.py`: busca dos trechos mais relevantes.
- `rag.py`: geração da resposta com Gemini.
- `app.py`: interface web em Streamlit.

Tecnologias:
- Python 3.11
- Streamlit
- LangChain
- Gemini
- Hugging Face / Sentence Transformers
- FAISS
- PyPDF
- Docker
- Oracle Cloud Infrastructure

Para execução local, instale as dependências:
python -m pip install -r requirements.txt

Recursos da interface:
- A interface permite:
- conversar com o agente;
- manter o contexto da conversa;
- visualizar as fontes utilizadas;
- avaliar respostas;
- iniciar uma nova conversa.

As respostas possuem caráter informativo e não substituem orientação jurídica profissional.

Manutenção:
A base de conhecimento deve ser atualizada sempre que houver uma nova versão dos documentos oficiais.
Fluxo de atualização: Documento atualizado → substituição do PDF → novo processamento → novos embeddings → reconstrução do índice FAISS → testes → novo deploy.

A qualidade do agente pode ser acompanhada observando:
- perguntas sem resposta;
- feedback negativo;
- tempo de resposta;
- dúvidas recorrentes com baixa qualidade de resposta.

Esses dados podem orientar ajustes no conteúdo, chunking, recuperação e prompt.

Docker e OCI:
O projeto possui Dockerfile para implantação em nuvem.
A arquitetura prevista para produção é:
Docker → OCI Container Registry → OCI Container Instance.

Testes realizados:
Foram validados cenários como
- definição de consumidor;
- produto com defeito;
- continuidade de conversa;
- pergunta fora do escopo;
- exibição de fontes;
- feedback positivo e negativo.

Registro de execução
As execuções do agente são registradas em JSON nos logs do ambiente em nuvem, contendo:

- timestamp
- pergunta
- resposta
- fontes recuperadas
- tempo de resposta.
