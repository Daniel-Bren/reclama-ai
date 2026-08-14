RECLAMA AI

Agente de Inteligência Artificial para consulta de direitos do consumidor.

Projeto desenvolvido como parte do Alura Agent do programa Oracle ONE Next Generation 2026.

O projeto

Um agente de IA criado para responder dúvidas sobre direitos do consumidor com base em documentos oficiais.
O sistema utiliza uma arquitetura RAG — Retrieval-Augmented Generation, combinando busca semântica em documentos com um modelo de linguagem.

A proposta é permitir que o usuário faça perguntas em linguagem natural.

O agente busca os trechos mais relevantes da legislação, envia esse contexto ao modelo de linguagem e gera uma resposta simples, citando as fontes utilizadas.

* O RECLAMA AI possui caráter informativo e não substitui orientação jurídica profissional.

Problema
A legislação de defesa do consumidor contém muitas informações importantes, mas nem sempre é fácil para o usuário localizar o artigo ou interpretar o texto jurídico.
O RECLAMA AI busca reduzir essa dificuldade oferecendo uma interface conversacional capaz de consultar os documentos e explicar o conteúdo em linguagem mais acessível.

Solução
O projeto utiliza IA generativa combinada com recuperação semântica de documentos.

Pergunta do usuário -> Busca semântica -> FAISS -> Trechos relevantes do CDC -> Prompt com contexto -> Gemini -> Resposta com fontes
