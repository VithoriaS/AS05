# 🤖 Assistente Inteligente de PDFs com Gemini e Pinecone

Este projeto cria um assistente que responde perguntas com base no conteúdo de arquivos PDF utilizando **Google Gemini**, **Pinecone** e **LangChain**. A interface é feita com **Gradio** para facilitar a interação via navegador.

---

## 🛠️ Instalação

Certifique-se de ter o Python 3.10+ instalado. Em seguida, instale as dependências com:

```bash
pip install gradio python-dotenv PyPDF2 pinecone-client google-generativeai langchain langchain-pinecone langchain-huggingface
```

---

## ⚙️ Configuração

Renomeie o arquivo `env.` para `.env`:

> 📝 Substitua os valores entre `<...>` pelas suas chaves reais das plataformas [Pinecone](https://www.pinecone.io/) e [Google AI Studio (Gemini)](https://aistudio.google.com/).
---

## 🚀 Executando o Projeto

Depois de configurar o `.env` e adicionar seus arquivos PDF:

```bash
python main.py
```

O Gradio abrirá uma interface no navegador onde você pode digitar perguntas com base no conteúdo dos documentos carregados.

---

## 🧠 Tecnologias Utilizadas

- **Google Gemini** – Geração de respostas baseadas em contexto.
- **Pinecone** – Armazenamento vetorial para buscas semânticas.
- **LangChain** – Gerenciamento de documentos, embeddings e prompts.
- **Gradio** – Interface web simples e interativa.
- **HuggingFace Embeddings** – Vetorização dos textos (modelo `all-MiniLM-L6-v2`).

---

## 📝 Exemplo de Uso

1. Adicione um PDF com um conteúdo, como um capítulo de um livro.
2. Pergunte:  
   **"Qual o autor do livro?"**
3. O assistente usará o Gemini para responder com base no texto extraído do PDF.

---

## 📌 Observações

- A indexação pode demorar alguns segundos, dependendo da quantidade e tamanho dos PDFs.
- A aplicação busca por trechos relevantes para cada pergunta e os usa como base para a resposta gerada.
