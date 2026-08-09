# ventura.system

![Status](https://img.shields.io/badge/status-adaptive%20orchestrator-blueviolet)
![License](https://img.shields.io/github/license/venturalabs-ai/ventura.system)

**Control plane experimental para roteamento multimodelo orientado por qualidade, custo, latência, risco e economia de contexto.**

## Objetivo

`ventura.system` transforma o método Ventura em componentes executáveis para decidir **quando usar ferramenta determinística, quando chamar um LLM, qual modelo usar e quando convocar um segundo modelo independente**.

A arquitetura não promete autonomia absoluta nem determinismo de LLM. Ela busca **autonomia máxima verificável**, com orçamento explícito, early-exit, telemetria e gates para operações de alto impacto.

## Componentes implementados

- `ventura_system/router.py` — ranking de modelos, estimativa de custo e seleção champion/challenger;
- `ventura_system/context.py` — compilação de contexto mínimo para evitar envio do repositório inteiro;
- `ventura_system/telemetry.py` — métricas JSONL de custo, tokens, latência, retries e eval score;
- `config/model-registry.json` — registry versionado de modelos e capacidades;
- `config/provider-costs.json` — fontes e cadência de atualização de preços;
- `config/routing-policy.json` — budgets, limites de modelos e hard gates;
- `scripts/benchmark_router.py` — benchmark determinístico do roteador;
- `tests/test_router.py` — testes funcionais de budget, challenger, contexto e telemetria.

## Política de execução

Fluxo recomendado:

```text
TASK
  -> tool-first check
  -> context compiler
  -> budget/policy gate
  -> model router
  -> champion
  -> challenger somente quando risco/incerteza justificar
  -> tool execution
  -> validator/evals
  -> telemetry
```

Perfis iniciais de orçamento:

| Perfil | Custo máximo/tarefa | Máx. modelos |
|---|---:|---:|
| simple | US$ 0,02 | 1 |
| normal | US$ 0,20 | 2 |
| critical | US$ 2,00 | 3 |

São defaults de engenharia, não autorização para gastar. Aplicações consumidoras podem aplicar limites menores.

## Registry multimodelo

O registry cobre estruturalmente 10 provedores. Modelos com preço/capacidade verificados podem ser habilitados. Provedores ainda sem dados oficiais verificados no ciclo de atualização permanecem `enabled: false` até discovery/validação, evitando inventar preço ou modelo.

Qualidade e latência do registry são **priors de roteamento**, não benchmarks universais. A evolução correta é substituí-los por resultados observados em evals versionados por tipo de tarefa.

## Economia de tokens

1. ferramenta determinística antes de LLM;
2. recuperar somente arquivos/símbolos relacionados;
3. reutilizar prefixos estáveis/cacheáveis;
4. modelo econômico para tarefas simples;
5. early-exit quando validação já é suficiente;
6. challenger apenas para risco/incerteza;
7. registrar custo real e sucesso para recalibrar o router.

## Hard gates

A política marca para controle reforçado ações como force-push, redução de proteções, alteração de secrets, deployment destrutivo, override de orçamento e ações financeiras irreversíveis.

## Testar

```bash
python -m pytest -q
python scripts/benchmark_router.py
```

O CI usa Actions pinadas por SHA e executa compile, testes funcionais e benchmark de smoke.

## Segurança

`ventura.system` decide rotas; autorização, DLP, credenciais, sandbox e políticas de execução devem ser aplicados pela camada de segurança, como `Ventura.SEG`, e pelas próprias ferramentas.

## Licença

Consulte [LICENSE](LICENSE). Referências externas mantêm seus próprios termos.
