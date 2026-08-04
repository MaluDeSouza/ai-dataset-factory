# AI Dataset Factory - Arquitetura da Plataforma

> **Versão:** 1.0
> **Status:** Arquitetura Base
> **Objetivo:** Definir a arquitetura técnica, responsabilidades dos componentes e fluxo de processamento do AI Dataset Factory.

---

# 1. Visão Geral

O **AI Dataset Factory** é uma plataforma de Engenharia de Dados para Inteligência Artificial responsável por transformar grandes volumes de documentos corporativos heterogêneos em ativos prontos para Fine Tuning e sistemas RAG (Retrieval-Augmented Generation).

Ao invés de focar no treinamento de modelos, o projeto resolve a etapa anterior: **preparação, organização e validação dos dados**.

Seu objetivo é reduzir drasticamente o esforço necessário para transformar informações desestruturadas em datasets de alta qualidade.

---

# 2. Objetivos do Projeto

O projeto foi concebido para atender organizações que desejam desenvolver modelos privados de IA utilizando seus próprios dados.

Entre os principais objetivos estão:

* Importação de documentos provenientes de múltiplas fontes.
* Padronização de formatos heterogêneos.
* Limpeza automática dos dados.
* Anonimização de informações sensíveis.
* Classificação inteligente dos documentos.
* Preparação de datasets para Fine Tuning.
* Preparação de bases vetoriais para sistemas RAG.
* Validação automática da qualidade dos dados.
* Exportação para formatos compatíveis com o ecossistema Hugging Face.

---

# 3. Escopo

O AI Dataset Factory **não realiza treinamento de modelos**.

Seu papel termina quando os dados encontram-se devidamente preparados para consumo por plataformas de treinamento ou mecanismos de busca vetorial.

---

# 4. Arquitetura Geral

```text
                  +----------------------+
                  |    Data Sources      |
                  +----------------------+
                             |
                             ▼
                  +----------------------+
                  |  Import Pipeline     |
                  +----------------------+
                             |
                             ▼
                  +----------------------+
                  | Normalization Layer  |
                  +----------------------+
                             |
                             ▼
                  +----------------------+
                  | Cleaning Pipeline    |
                  +----------------------+
                             |
                             ▼
                  +----------------------+
                  | Classification       |
                  +----------------------+
                             |
                             ▼
                  +----------------------+
                  | Validation Pipeline  |
                  +----------------------+
                    │                 │
          JSONL     │                 │ Embeddings
                    ▼                 ▼
          Fine Tuning          Vector Databases
```

---

# 5. Princípios Arquiteturais

A plataforma foi construída seguindo os seguintes princípios:

## Modularidade

Cada etapa do processamento é implementada como um módulo independente.

Nenhum componente possui conhecimento sobre a implementação interna dos demais.

---

## Pipeline Orientado a Etapas

Todo documento percorre uma sequência previsível de transformações.

Cada estágio recebe um objeto padronizado e devolve o mesmo objeto enriquecido.

Isso torna o pipeline facilmente extensível.

---

## Baixo Acoplamento

Toda integração externa ocorre através de interfaces.

Exemplos:

* LLM Provider
* Embedding Provider
* Storage Provider
* OCR Provider

Dessa forma novos provedores podem ser adicionados sem alterar regras de negócio.

---

## Processamento Assíncrono

Operações custosas são executadas por workers independentes.

Exemplos:

* OCR
* Chunking
* Embeddings
* Classificação
* Análise por LLM

Isso evita bloqueios da API e melhora escalabilidade.

---

## Arquitetura Evolutiva

Embora inicialmente implementado como um monólito modular, todos os módulos foram projetados para futura extração como microserviços.

---

# 6. Organização do Projeto

```text
src/

├── api/
│
├── application/
│
├── domain/
│
├── infrastructure/
│
├── workers/
│
├── shared/
│
└── config/
```

---

# 7. Responsabilidade das Camadas

## API

Responsável apenas por receber requisições HTTP.

Não contém regras de negócio.

Exemplos:

* Upload de documentos
* Consulta de datasets
* Exportação
* Monitoramento

---

## Application

Implementa os casos de uso do sistema.

Exemplos:

* ImportDatasetUseCase
* ProcessDatasetUseCase
* ExportDatasetUseCase
* GenerateEmbeddingsUseCase

Esta camada coordena o pipeline.

---

## Domain

Representa o núcleo da aplicação.

Contém:

* Entidades
* Objetos de valor
* Interfaces
* Regras de domínio

Nenhuma dependência externa deve existir nesta camada.

---

## Infrastructure

Implementações concretas.

Exemplos:

* PostgreSQL
* Qdrant
* FAISS
* Ollama
* Gemini
* OpenAI
* Filesystem

---

## Workers

Executam tarefas pesadas.

Exemplos:

* OCR
* Embeddings
* Sanitização
* Chunking
* Validação

---

# 8. Pipeline de Processamento

Todo documento percorre o seguinte fluxo.

```text
Import

↓

Normalization

↓

Cleaning

↓

Anonymization

↓

Classification

↓

Deduplication

↓

Chunking

↓

Validation

↓

Export
```

Cada etapa é independente.

---

# 9. Import Pipeline

Responsável pela ingestão dos dados.

Fontes suportadas:

* TXT
* PDF
* DOCX
* Markdown
* HTML
* CSV
* JSON
* Conversas exportadas
* Bases documentais

Todos os formatos são convertidos para um modelo interno comum.

---

# 10. Normalization Layer

Padroniza documentos provenientes de diferentes origens.

Entre as atividades:

* Normalização de encoding
* Conversão para UTF-8
* Remoção de caracteres inválidos
* Padronização de quebras de linha

---

# 11. Cleaning Pipeline

Responsável pela limpeza dos documentos.

Exemplos:

* Emojis
* Assinaturas
* Mensagens automáticas
* Rodapés
* URLs
* Cabeçalhos repetidos
* Espaços excedentes

O objetivo é preservar apenas conteúdo semanticamente relevante.

---

# 12. Anonymization Pipeline

Remove informações sensíveis antes do treinamento.

Exemplos:

* CPF
* CNPJ
* Telefones
* Emails
* Endereços
* Dados pessoais

A implementação poderá utilizar duas camadas complementares:

* Regras determinísticas (Regex)
* Modelos de linguagem para anonimização contextual

---

# 13. Classification Pipeline

Classifica automaticamente os documentos.

Exemplos de categorias:

* Conversa
* FAQ
* Manual
* Política
* Contrato
* Tutorial
* Log
* Código

A classificação determina qual processamento será realizado posteriormente.

---

# 14. Chunking Pipeline

Responsável por dividir documentos longos em blocos semanticamente coerentes.

Os chunks produzidos podem ser utilizados tanto para geração de embeddings quanto para sistemas RAG.

---

# 15. Validation Pipeline

Executa verificações automáticas de qualidade.

Exemplos:

* JSON inválido
* Duplicidade
* Conversas incompletas
* Respostas vazias
* Tokens excessivos
* Exemplos contraditórios
* Dados incompletos

Ao final é produzido um relatório de qualidade.

---

# 16. Export Pipeline

Converte os dados processados para formatos externos.

Exemplos:

* JSONL (Fine Tuning)
* JSON
* CSV
* Markdown estruturado

---

# 17. Sistema de Providers

Todas as integrações externas são abstraídas.

## LLM Provider

Responsável por operações envolvendo modelos de linguagem.

Implementações possíveis:

* Gemini
* Ollama
* OpenAI
* OpenRouter

---

## Embedding Provider

Responsável pela geração de embeddings.

Implementações possíveis:

* BGE
* E5
* FastEmbed
* Sentence Transformers

---

## Storage Provider

Responsável pelo armazenamento.

Implementações possíveis:

* Local
* S3
* MinIO
* Google Cloud Storage

---

# 18. Modelo de Dados

O domínio é composto por entidades que representam o ciclo de vida do processamento.

Principais entidades:

* Dataset
* Document
* Chunk
* Embedding
* ProcessingJob
* ValidationReport
* ExportArtifact

Cada entidade possui responsabilidade única e representa um estágio do pipeline.

---

# 19. Escalabilidade

A arquitetura permite evolução gradual.

Inicialmente:

* Monólito Modular
* Banco PostgreSQL
* Processamento Local

Evolução futura:

* RabbitMQ
* Redis Streams
* Kubernetes
* Workers distribuídos
* Microserviços independentes

Nenhuma alteração significativa nas regras de negócio será necessária para essa transição.

---

# 20. Fluxo Completo

```text
Documentos

↓

Importação

↓

Normalização

↓

Limpeza

↓

Anonimização

↓

Classificação

↓

Chunking

↓

Validação

├───────────────┐
│               │
▼               ▼

JSONL       Embeddings

▼               ▼

Fine Tuning    RAG
```

---

# 21. Filosofia do Projeto

O AI Dataset Factory parte do princípio de que **a qualidade de um modelo de IA é diretamente influenciada pela qualidade dos dados utilizados em sua construção**.

Enquanto a maior parte das ferramentas concentra esforços no treinamento dos modelos, esta plataforma dedica-se à etapa frequentemente mais custosa e negligenciada: a engenharia de dados para Inteligência Artificial.

Ao separar ingestão, preparação, validação e exportação em componentes independentes, o projeto estabelece uma base reutilizável para qualquer pipeline moderno de Fine Tuning ou RAG, permitindo que empresas transformem conhecimento corporativo em ativos prontos para modelos privados de IA de forma segura, escalável e reproduzível.
