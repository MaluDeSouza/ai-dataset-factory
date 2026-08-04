# Roadmap de Desenvolvimento: AI Dataset Factory

## Fase 1: Fundação e Estrutura Base
O objetivo aqui é criar o esqueleto do projeto seguindo a organização proposta, garantindo que a modularidade e o isolamento sejam respeitados desde o primeiro commit.

* **Branch:** `feat/setup-base-architecture`
* **Tarefas:**
  * Criar a estrutura de diretórios base: `api/`, `application/`, `domain/`, `infrastructure/`, `workers/`, `shared/` e `config/`.
  * Configurar o ambiente (dependências principais de validação estrutural, como Pydantic, e linters).
  * Criar um ponto de entrada básico apenas para validar a execução.

# Fase 2 — Modelo de Domínio e Persistência

Nesta etapa o projeto passa a possuir entidades reais e persistência de dados. O objetivo é abandonar estruturas temporárias e estabelecer a base sobre a qual todo o pipeline será construído.

**Branch:** `feat/domain-and-persistence`

## Objetivos

- Modelar as principais entidades do domínio:
  - Dataset
  - Document
  - Chunk
  - ProcessingJob
- Implementar validação consistente utilizando Pydantic.
- Configurar SQLAlchemy e PostgreSQL.
- Criar a estrutura inicial do banco de dados.
- Implementar um `StorageProvider` funcional utilizando o sistema de arquivos local.

---

# Fase 3 — Pipeline de Ingestão e Limpeza

Com a persistência pronta, o próximo passo é permitir que documentos reais sejam processados pelo sistema.

**Branch:** `feat/pipeline-ingestion-cleaning`

## Objetivos

- Implementar o Import Pipeline.
- Suportar inicialmente:
  - TXT
  - PDF
- Converter documentos para o modelo interno da aplicação.
- Implementar a camada de normalização:
  - UTF-8
  - Espaços
  - Quebras de linha
- Desenvolver o Cleaning Pipeline utilizando regras determinísticas (Regex).
- Criar testes simples validando documentos reais.

---

# Fase 4 — Pipeline de Processamento Inteligente

Nesta fase a plataforma passa a utilizar modelos de linguagem para enriquecer automaticamente os dados processados.

**Branch:** `feat/pipeline-rag-intelligence`

## Objetivos

- Integrar um `LLMProvider`.
- Implementar o Classification Pipeline.
- Implementar anonimização contextual utilizando IA.
- Desenvolver o Chunking Pipeline.
- Integrar um `EmbeddingProvider`.
- Gerar embeddings dos documentos processados.

---

# Fase 5 — Casos de Uso e API

Com todos os módulos funcionando isoladamente, a aplicação passa a expor seus recursos através de uma API REST.

**Branch:** `feat/application-and-api`

## Objetivos

- Implementar os principais Use Cases.
- Orquestrar os pipelines através da camada Application.
- Desenvolver a API utilizando FastAPI.
- Disponibilizar endpoints para:
  - Upload de documentos
  - Consulta de processamento
  - Consulta de datasets
  - Gerenciamento de arquivos
- Garantir que a camada HTTP não contenha regras de negócio.

---

# Fase 6 — Validação, Exportação e Processamento Assíncrono

A última etapa transforma a plataforma em uma solução pronta para utilização em projetos reais.

**Branch:** `feat/validation-export-workers`

## Objetivos

- Implementar o Validation Pipeline.
- Detectar:
  - Documentos duplicados
  - Chunks inválidos
  - Dados inconsistentes
- Gerar datasets em JSONL para Fine Tuning.
- Adicionar suporte para futuras exportações.
- Executar tarefas pesadas em background:
  - OCR
  - Embeddings
  - Chunking
  - Processamento por LLM
- Garantir que a API permaneça responsiva durante todo o processamento.

---

# Fase 7 — Observabilidade e Dashboard (Roadmap Futuro)

Após a conclusão do MVP, a plataforma poderá evoluir para oferecer recursos de monitoramento e acompanhamento do pipeline.

**Branch:** `feat/observability-dashboard`

## Objetivos

- Dashboard de processamento.
- Histórico de execuções.
- Barra de progresso dos jobs.
- Estatísticas do dataset.
- Relatórios de qualidade.
- Visualização de chunks.
- Monitoramento de embeddings.
- Logs estruturados.
- Métricas de processamento.

---

# Visão Geral do Roadmap

```text
Fase 1
Setup e Estrutura Base
        │
        ▼
Fase 2
Modelo de Domínio e Persistência
        │
        ▼
Fase 3
Pipeline de Ingestão e Limpeza
        │
        ▼
Fase 4
Pipeline de Processamento Inteligente
        │
        ▼
Fase 5
Casos de Uso e API
        │
        ▼
Fase 6
Validação, Exportação e Workers
        │
        ▼
Fase 7
Observabilidade e Dashboard
```

## Filosofia de Desenvolvimento

Cada fase entrega uma funcionalidade utilizável da plataforma, permitindo evolução incremental, validação contínua da arquitetura e redução da complexidade durante o desenvolvimento.

A arquitetura foi projetada para evoluir inicialmente como um **Monólito Modular**, preservando baixo acoplamento entre os componentes e permitindo futura migração para uma arquitetura baseada em microserviços sem alterações significativas nas regras de negócio.