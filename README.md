# ventura.system

![MIT](https://img.shields.io/github/license/chamseddinehiddoud/ventura.system)
![stars](https://img.shields.io/github/stars/chamseddinehiddoud/ventura.system)
![forks](https://img.shields.io/github/forks/chamseddinehiddoud/ventura.system)

Versão **Ventura** do clássico *system-design-primer* — guia curado de design
de sistemas para entrevistas e arquitetura, com uma skill de replay
determinístico para desenhar soluções sem partir do zero a cada vez.

> **Curadoria original** — este repositório organiza conceitos e o método de
> design de forma própria; o conteúdo completo de referência vive no projeto
> original (system-design-primer).

## O que é

Fundamentos de arquitetura (escala, cache, filas, dados, consistência) e um
método de 6 passos para desenhar qualquer sistema. A skill `SKILL.md`
transforma o processo em receita determinística.

## Conceitos-chave

| Conceito | Pergunta que responde |
|---|---|
| **Escala** | como o sistema se comporta com mais usuários/dados |
| **Balanceamento** | como distribuir carga entre servidores |
| **Cache** | como evitar trabalho repetido |
| **Filas / assíncrono** | como desacoplar e absorver picos |
| **Banco de dados** | relacional vs. não-relacional, indexação |
| **Consistência** | forte vs. eventual; trade-offs |
| **Replicação / partição** | como manter dados disponíveis e distribuídos |
| **Observabilidade** | métricas, logs, traces, alertas |

## Método de design (6 passos)

| Passo | Entregável |
|---|---|
| **1. Requisitos** | funcional + não-funcional, usuários, volume |
| **2. Estimativas** | QPS, armazenamento, largura de banda |
| **3. Blocos** | diagrama de alto nível (clients, serviços, dados) |
| **4. Dados** | modelo, banco, schema, índices |
| **5. Detalhes** | cache, filas, consistência, replicação |
| **6. Trade-offs** | riscos, gargalos, evolução |

## Como usar (com a skill)

```text
1. Modo EXPLORE  — leia os requisitos e estimativas do problema (uma vez)
2. Modo COMPILE  — registre o desenho em sistema.md (blocos, dados, trade-offs)
3. Modo REPLAY   — reutilize o desenho em sistemas similares, ajustando detalhes
4. Modo REGENERATE — requisito novo (escala/consistência) → regenere o desenho
```

## Licença

MIT License — Copyright (c) 2026 Wemerson Mota de Oliveira.
