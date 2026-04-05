import os
import glob
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

class PepsicoRAG:
    def __init__(self, kb_path="knowledge_base"):
        self.kb_path = kb_path
        self.vector_store_path = "faiss_index_v4"
        self.vector_store = None
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1)
        self.embeddings = OpenAIEmbeddings()
        self.init_rag()

    def init_rag(self):
        if os.path.exists(self.vector_store_path):
            self.vector_store = FAISS.load_local(self.vector_store_path, self.embeddings, allow_dangerous_deserialization=True)
            return

        documents = []
        pdf_files = glob.glob(os.path.join(self.kb_path, "*.pdf"))
        
        for pdf_file in pdf_files:
            try:
                loader = PyPDFLoader(pdf_file)
                docs = loader.load()
                documents.extend(docs)
            except Exception as e:
                pass
        
        mock_text = (
            "Playbook Pepsico Bogotá: \n"
            "Regla 1: Si la caída de Market Share es crítica (> 7%), aplicar 'Nivel GAMMA' (Intervención Extrema).\n"
            "Regla 2: Fallos Logísticos o OSA bajos con Share decayendo: aplicar 'Nivel BETA' (Reestructuración Zonal).\n"
            "Regla 3: Si todo es normal pero hay oportunidad: aplicar 'Nivel ALFA' (Optimización de Rutina).\n"
            "Regla 4: El precio umbral de 30g es $2.500 COP. Cruzarlo sin avisar arruina el Sentimiento del Tendero.\n"
        )
        if not documents:
            from langchain.schema import Document
            documents.append(Document(page_content=mock_text))

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(documents)
        self.vector_store = FAISS.from_documents(splits, self.embeddings)
        self.vector_store.save_local(self.vector_store_path)

    def orquestar_debate(self, logs_memoria: list):
        if not logs_memoria: return "Nivel ALFA. Flujo normal."
        estado_unido = "\n".join([f"  - {l}" for l in logs_memoria])
        
        template = """Eres el Strategic_Orchestrator de Pepsico para Colombia.
Reporte de memoria cruzada (Analista y Sentinel):
{contexto_agentes}

Contexto RAG:
{context}

PRECAUCIÓN: Estás OBLIGADO a sintetizar reportes, considerar el OSA y dictaminar el Nivel ALFA, BETA o GAMMA del Playbook.
Tu respuesta debe ser directiva y mencionar ALFA, BETA o GAMMA obligatoriamente.
Evaluación:"""
        retriever = self.vector_store.as_retriever()
        prompt = PromptTemplate.from_template(template)
        document_chain = create_stuff_documents_chain(self.llm, prompt)
        retrieval_chain = create_retrieval_chain(retriever, document_chain)
        return retrieval_chain.invoke({"input": "Orquesta debate e indica nivel táctico.", "contexto_agentes": estado_unido})["answer"]

    def responder_consulta(self, memoria_activa: list, log_chat_previo: list, pregunta_gerente: str):
        estado_unido = "\n".join([f"- {l}" for l in memoria_activa[-8:]]) if memoria_activa else "Sin métricas."
        chat_unido = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in log_chat_previo[-4:]]) if log_chat_previo else "Sin historial."
        
        template = """Eres un Senior AI Solutions Architect operando el Pepsico Strategy Room.
Memoria Activa:
{contexto_agentes}
Historial Chat: {historial_chat}
Contexto RAG: {context}

Usuario pide: {input}

REGLAS DE SALIDA OBLIGATORIAS (JSON CONTROL):
Siempre, al final de tu respuesta textual, DEBES adjuntar obligatoriamente el siguiente bloque JSON:
```json
{{
  "is_simulation": <true o false>,
  "objetivo_alcanzado_estimado": <NUMERO_O_NULL>
}}
```
- Escribe "is_simulation": true ÚNICAMENTE si el gerente pide expresamente visualizar, simular o predecir un escenario a futuro ('¿Qué pasa si...?', 'simula', 'proyecta'). Si no es el caso, DEBES poner false.
- Si pones true, en "objetivo_alcanzado_estimado" debes inferir lógicamente el porcentaje de market share (ej 52.5 o 60.3). Si pones false, pon null.
"""
        retriever = self.vector_store.as_retriever()
        prompt = PromptTemplate.from_template(template)
        document_chain = create_stuff_documents_chain(self.llm, prompt)
        retrieval_chain = create_retrieval_chain(retriever, document_chain)
        
        return retrieval_chain.invoke({
            "input": pregunta_gerente,
            "contexto_agentes": estado_unido,
            "historial_chat": chat_unido
        })["answer"]
