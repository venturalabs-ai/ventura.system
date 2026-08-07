# Skill: ventura.system — LOOP Skill Engine / Constrained Replay

![License](https://img.shields.io/github/license/venturalabs-ai/ventura.system)
![Stars](https://img.shields.io/github/stars/venturalabs-ai/ventura.system)

Skill de design de sistemas com **replay restrito por desenho versionado**: explore requisitos quando necessário, compile decisões, reutilize artefatos compatíveis e regenere quando escala ou requisitos mudarem.

## Trigger

Use quando o usuário quiser desenhar um sistema, preparar entrevista de system design, revisar trade-offs, estimar capacidade ou dimensionar infraestrutura.

## Arquitetura de eficiência

| Fase | Descrição | Meta de contexto |
|---|---|---|
| **Explore** | Analisa requisitos e estimativas | Maior |
| **Compile** | Gera `sistema.md`: blocos, dados, decisões e trade-offs | Reduzida |
| **Constrained Replay** | Reutiliza apenas decisões compatíveis com o novo caso | Mínima necessária |
| **Regenerate** | Reavalia quando escala, SLA ou requisitos mudarem | Sob demanda |

O consumo real de tokens depende do modelo, runtime, contexto e ferramentas. Este projeto não afirma execução com zero tokens nem determinismo de saídas LLM.

## Receita de replay

```text
1. PEDIDO   — desenhar ou revisar sistema
2. RECEITA  — consulta sistema.md: blocos, dados, detalhes e trade-offs
3. EXECUTA  — requisitos | estimativas | blocos | dados | detalhes
4. REGISTRA — decisões, riscos, gargalos e evolução
5. STOP-YIELD — mudança relevante de requisito → regenerar
```

## Regras de engenharia

- definir token/context budget mensurável por runtime;
- limitar o replay ao desenho compilado necessário;
- usar prefixos estáveis somente quando o provedor/runtime oferecer cache compatível;
- versionar decisões e trade-offs;
- voltar ao Explore quando requisitos mudarem materialmente.

## Compilar o desenho

```text
1. Levante requisitos funcionais e não funcionais, volume e SLA.
2. Estime QPS, armazenamento e largura de banda em ordem de grandeza.
3. Registre sistema.md com blocos, dados, cache, filas e consistência.
4. Documente trade-offs e inicie Constrained Replay.
```
