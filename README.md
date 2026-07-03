# Pipefy RAG Chat

Case técnico para a vaga **Software Engineer Pleno — Data & AI (Generalista)**.

A aplicação permite o upload de documentos e interação via chat utilizando uma arquitetura **RAG — Retrieval-Augmented Generation** com busca semântica, embeddings open-source, Redis Vector Search, FastAPI, LangGraph e React.

---

## Visão geral

O projeto implementa uma solução full-stack de chat com documentos.

Fluxo principal:

1. Upload de arquivos PDF, TXT e DOCX.
2. Extração de texto dos documentos.
3. Chunking com overlap configurável.
4. Geração de embeddings com Sentence Transformers.
5. Indexação vetorial no Redis Stack com RedisSearch.
6. Busca semântica dos trechos mais relevantes.
7. Pipeline RAG orquestrado com LangGraph.
8. Resposta conversacional com fontes utilizadas.
9. Interface React para upload, documentos, sessões e chat.

---

## Stack

| Camada | Tecnologia |
|---|---|
| Backend | FastAPI |
| Frontend | React + Vite |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| LLM | Ollama + llama3.1:8b |
| Vector Store | Redis Stack / RedisSearch |
| Orquestração RAG | LangGraph |
| Testes | pytest + pytest-cov |
| Infraestrutura | Docker Compose |
| CI | GitHub Actions |

---

## Arquitetura

```txt
Usuário
↓
Frontend React
↓
FastAPI
↓
Upload / Chat / Documents
↓
Pipeline de ingestão
↓
Loader PDF/TXT/DOCX
↓
Chunking
↓
Embeddings
↓
Redis Vector Search
↓
Retriever
↓
LangGraph RAG Pipeline
↓
LLM / Ollama
↓
Resposta + Sources
```

---

## Fluxo LangGraph

O pipeline de RAG foi implementado com LangGraph seguindo o fluxo:

```txt
START
↓
retriever_node
↓
context_builder_node
↓
llm_node
↓
response_formatter_node
↓
END
```

Cada nó possui uma responsabilidade clara:

| Nó | Responsabilidade |
|---|---|
| `retriever_node` | Busca os chunks semanticamente relevantes |
| `context_builder_node` | Monta contexto, histórico e prompt |
| `llm_node` | Chama o modelo de linguagem |
| `response_formatter_node` | Formata a resposta final e as fontes |

---

## Endpoints

| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/health` | Health check da API e Redis |
| POST | `/upload` | Upload e ingestão de documento |
| GET | `/documents` | Lista documentos indexados |
| GET | `/documents/{file_id}/chunks` | Lista chunks de um documento |
| DELETE | `/documents/{file_id}` | Remove documento e vetores |
| POST | `/search` | Executa busca semântica para debug |
| POST | `/chat` | Chat com RAG |

---

## Rodando com Docker Compose

Crie o arquivo `.env` a partir do exemplo:

```bash
cp .env.example .env
```

No Windows PowerShell:

```powershell
copy .env.example .env
```

Depois suba os serviços:

```bash
docker compose up --build
```

Serviços disponíveis:

| Serviço | URL |
|---|---|
| Frontend | http://localhost:3000 |
| API | http://localhost:8000 |
| Swagger | http://localhost:8000/docs |
| RedisInsight | http://localhost:8001 |
| Ollama | http://localhost:11434 |

Para baixar o modelo do Ollama:

```bash
docker compose exec ollama ollama pull llama3.1:8b
```

> Importante: caso o modelo do Ollama ainda não esteja disponível, a API continua respondendo com fallback local baseado no trecho mais relevante recuperado pelo pipeline RAG.

---

## Rodando localmente sem Docker

Caso tenha problemas com Docker, também é possível rodar backend e frontend localmente.

### Backend

Linux/macOS:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --reload-dir app --host 127.0.0.1 --port 8000
```

Windows PowerShell:

```powershell
cd backend
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --reload-dir app --host 127.0.0.1 --port 8000
```

A API ficará disponível em:

```txt
http://127.0.0.1:8000
```

Swagger:

```txt
http://127.0.0.1:8000/docs
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Acesse:

```txt
http://localhost:5173
```

---

## Variáveis de ambiente

| Variável | Descrição |
|---|---|
| `REDIS_URL` | URL de conexão com Redis |
| `REDIS_REQUIRED` | Define se Redis é obrigatório para a API funcionar |
| `REDIS_INDEX_NAME` | Nome do índice vetorial no Redis |
| `REDIS_KEY_PREFIX` | Prefixo das chaves salvas no Redis |
| `EMBEDDING_MODEL` | Modelo usado para gerar embeddings |
| `EMBEDDING_DIMENSION` | Dimensão dos vetores de embedding |
| `OLLAMA_BASE_URL` | URL do serviço Ollama |
| `OLLAMA_MODEL` | Modelo LLM usado pelo Ollama |
| `CHUNK_SIZE` | Tamanho dos chunks |
| `CHUNK_OVERLAP` | Overlap entre chunks |
| `TOP_K` | Quantidade padrão de chunks recuperados |
| `VITE_API_URL` | URL da API usada pelo frontend |

Exemplo:

```env
APP_NAME=Pipefy RAG Chat API
APP_ENV=local
DEBUG=true

REDIS_URL=redis://redis:6379
REDIS_REQUIRED=false
REDIS_INDEX_NAME=idx:docs
REDIS_KEY_PREFIX=doc:

CORS_ORIGINS=http://localhost:3000,http://localhost:5173

EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384

OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama3.1:8b

CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K=5

VITE_API_URL=http://localhost:8000
```

---

## Testes

Rodar os testes do backend:

```bash
cd backend
pytest
```

Rodar testes com cobertura:

```bash
pytest --cov=app --cov-report=term-missing
```

Cobertura validada durante o desenvolvimento:

```txt
12 passed
76% coverage
```

---

## CI

O projeto possui GitHub Actions para executar os testes do backend a cada push e pull request.

Workflow:

```txt
.github/workflows/backend-ci.yml
```

---

## Diferenciais implementados

- Upload de múltiplos formatos: PDF, TXT e DOCX.
- Chunking com overlap configurável.
- Embeddings open-source com Sentence Transformers.
- Redis Vector Search com HNSW.
- Fallback em memória para ambiente local sem Redis.
- RAG com LangGraph.
- Histórico por sessão.
- Múltiplas sessões no frontend.
- Interface com paleta visual inspirada na Pipefy.
- Exibição das fontes usadas na resposta.
- Remoção de documentos.
- Testes automatizados com mocks.
- GitHub Actions.
- Docker Compose com API, frontend, Redis e Ollama.

---

## Decisões técnicas

### Sentence Transformers

Foi escolhido o modelo `sentence-transformers/all-MiniLM-L6-v2` por ser open-source, leve e gerar embeddings de 384 dimensões. Essa escolha reduz custo, evita dependência obrigatória de APIs pagas e permite rodar o pipeline localmente.

### Redis Stack

Redis Stack foi utilizado como banco vetorial por oferecer RedisSearch com suporte a índices vetoriais, HNSW e busca KNN.

### LangGraph

LangGraph foi utilizado para deixar o pipeline RAG explícito, modular e extensível. Essa abordagem facilita a evolução futura com retry, validação, branching condicional, streaming e outros nós especializados.

### Ollama

O Ollama foi escolhido para permitir uso de LLM local com `llama3.1:8b`, reduzindo dependência de provedores externos.

### Fallback local

Durante o desenvolvimento, Redis e Ollama podem estar indisponíveis. Por isso, a aplicação possui fallback em memória para busca semântica e fallback local de resposta quando o Ollama não está acessível.

Esse fallback facilita o desenvolvimento local sem comprometer a arquitetura final baseada em Redis e Ollama via Docker Compose.

---

## Trade-offs

- Documentos e sessões em memória são úteis para desenvolvimento, mas em produção deveriam ser persistidos em banco.
- O modelo local via Ollama reduz custo, mas pode ter performance inferior a modelos hospedados como GPT-4o ou Claude.
- Redis foi usado como vector store, mas metadados mais ricos poderiam ser persistidos em banco relacional.
- Streaming de resposta ainda não foi implementado, mas a arquitetura permite adicionar SSE ou WebSocket futuramente.

---

## Próximos passos

- Autenticação.
- Persistência de sessões.
- Streaming de respostas.
- Melhorias visuais no frontend.
- Deploy em nuvem.
- Observabilidade com logs estruturados.