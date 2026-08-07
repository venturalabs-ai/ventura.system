# Skill: ventura.system — LOOP Skill Engine / Deterministic Replay

![MIT](https://img.shields.io/github/license/chamseddinehiddoud/ventura.system)
![stars](https://img.shields.io/github/stars/chamseddinehiddoud/ventura.system)
![forks](https://img.shields.io/github/forks/chamseddinehiddoud/ventura.system)

Skill de design de sistemas com **execução determinística**: explore os
requisitos uma vez, compile o desenho, replique em sistemas similares com
~zero tokens, regenere quando a escala ou os requisitos mudarem.

## Trigger

Use quando o usuário quiser: desenhar um sistema, entrevista de system
design, arquitetar um serviço, revisar trade-offs, estimar capacidade,
dimensionar infraestrutura.

## Arquitetura Token-Efficient & Regenerative

| Fase | Descrição | Consumo |
|---|---|---|
| **Explore** | Modelo forte analisa requisitos + estimativas (uma vez) | Alto (único) |
| **Compile** | Gera `sistema.md`: blocos, dados, detalhes, trade-offs | Baixo |
| **Replay** | Reutiliza o desenho em sistemas similares | Mínimo/Zero |
| **Regenerate** | Escala/requisito mudou → regenere o desenho | Sob demanda |

## Receita determinística (Replay)

```text
1. PEDIDO   — "desenhar sistema X" | "revisar arquitetura Y"
2. RECEITA  — consulta sistema.md: blocos, modelo de dados, detalhes, trade-offs
3. EXECUTA  — 1. requisitos | 2. estimativas | 3. blocos | 4. dados | 5. detalhes
4. REGISTRA — decisões, riscos, gargalos, evolução
5. STOP-YIELD — requisito de escala/consistência estoura o desenho → regenerar
```

## Regras de engenharia

- **Token Budget** — Explore: até 8k tokens. Replay: < 300 tokens.
- **Context Firewall** — o replay só vê o desenho compilado (nunca o guia inteiro).
- **Prefix Caching** — o sistema deste arquivo fica byte-stable.
- **Skill Distillation** — desenho validado vira receita permanente.
- **Regeneração** — novo requisito de escala → volta ao Explore.

## Como compilar o desenho (Explore → Compile)

```text
1. Entrevista de requisitos: funcional, não-funcional, usuários, volume, SLA
2. Estima: QPS, armazenamento, largura de banda (ordem de grandeza)
3. Compila sistema.md: diagrama de blocos, dados, cache, filas, consistência
4. Documenta trade-offs e ativa o Replay
```

## Exemplo de uso

```text
Atue como ventura.system (modo REPLAY). Meu sistema.md é de um "encurtador de
URL". Aplique o desenho a um "serviço de QR code": o que muda em blocos,
dados e cache? Use menos de 300 tokens e registre os trade-offs.
```
