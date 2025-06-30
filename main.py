import os
import sys
import gradio as gr
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import google.generativeai as genai
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone as PineconeClient, ServerlessSpec

def criar_vectorstore(index, documentos: list[Document]):
    fatiador = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    partes = fatiador.split_documents(documentos)

    embedder = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"}
    )

    store = PineconeVectorStore(
        index=index,
        embedding=embedder,
        text_key="text",
        namespace="default"
    )
    store.add_documents(partes)
    return store, len(partes)

def carregar_configuracoes():
    load_dotenv()
    chaves = {
        "MY_PINECONE_API_KEY": os.getenv("MY_PINECONE_API_KEY"),
        "MY_PINECONE_INDEX_NAME": os.getenv("MY_PINECONE_INDEX_NAME"),
        "MY_PINECONE_CLOUD": os.getenv("MY_PINECONE_CLOUD"),
        "MY_PINECONE_REGION": os.getenv("MY_PINECONE_REGION"),
        "MY_GEMINI_API_KEY": os.getenv("MY_GEMINI_API_KEY"),
    }

    if not all(chaves.values()):
        print("Erro -> o arquivo .env esta sem as chaves.")
        sys.exit(1)

    return chaves

def inicializar_pinecone(api_key: str, index_name: str, cloud: str, region: str):
    cliente = PineconeClient(api_key=api_key)
    if index_name not in cliente.list_indexes().names():
        cliente.create_index(
            name=index_name,
            dimension=384,
            metric="cosine",
            spec=ServerlessSpec(cloud=cloud, region=region)
        )
    return cliente.Index(index_name)

def inicializar_gemini(api_key: str):
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemma-3-1b-it")

def criar_interface():
    with gr.Blocks() as interface:
        gr.Markdown("## Assistente de Dúvidas")
        gr.Markdown("Este assistente responde perguntas baseadas no conteúdo de pdfs. Faça sua pergunta:")

        with gr.Row():
            campo_pergunta = gr.Textbox(label="Sua pergunta", placeholder="Qual o autor?")
        campo_resposta = gr.Markdown(label="Resposta gerada")

        botao = gr.Button("Resposta")
        botao.click(fn=responder_pergunta, inputs=campo_pergunta, outputs=campo_resposta)

    return interface


def responder_pergunta(pergunta: str) -> str:
    resultados = retriever.get_relevant_documents(pergunta)
    contexto = "\n\n".join(doc.page_content for doc in resultados)

    prompt = f"""
    Você é um assistente treinado para responder perguntas com base em arquivos PDF.

    Com base no conteúdo abaixo, forneça uma resposta clara, objetiva e útil.

    --- Conteúdo extraído dos documentos ---
    {contexto}

    --- Pergunta ---
    {pergunta}

    Resposta:"""

    resposta = modelo_gemini.generate_content(prompt).text
    return resposta

def carregar_pdfs(pasta: str) -> list[Document]:
    documentos = []
    for arquivo in os.listdir(pasta):
        if arquivo.lower().endswith(".pdf"):
            caminho = os.path.join(pasta, arquivo)
            leitor = PdfReader(caminho)
            texto = "".join(pagina.extract_text() or "" for pagina in leitor.pages)
            documentos.append(Document(page_content=texto, metadata={"fonte": arquivo}))
    return documentos

if __name__ == "__main__":
    config = carregar_configuracoes()

    modelo_gemini = inicializar_gemini(config["MY_GEMINI_API_KEY"])
    indice_pinecone = inicializar_pinecone(
        api_key=config["MY_PINECONE_API_KEY"],
        index_name=config["MY_PINECONE_INDEX_NAME"], 
        cloud=config["MY_PINECONE_CLOUD"],
        region=config["MY_PINECONE_REGION"]
    )

    print("Carregando arquivo")
    documentos_brutos = carregar_pdfs("pdf")

    vectorstore, total_chunks = criar_vectorstore(indice_pinecone, documentos_brutos)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

    print(f"Finalizado o processamento! {total_chunks}")

    app = criar_interface()
    app.launch()