# GOLstory AI Radar

Automação n8n para o [GOLstory.com.br](https://golstory.com.br), hospedado no VPS
Hostinger `srv1925412.hstgr.cloud` (Ubuntu 24.04, Docker + Traefik já instalados).

## Nota legal e editorial (leia antes de ativar)

Reescrever/traduzir integralmente matérias de terceiros e publicá-las como
autoria de uma pessoa real, sem crédito à fonte, é violação de direitos
autorais e falsa atribuição de autoria — isso **não** está implementado aqui.
Este pacote usa dois formatos legítimos:

1. **Radar IA** (`workflow-radar-noticias.json`) — agregador de notícias:
   resumo curto e neutro (parafraseado, nunca copiado), sempre com link e
   crédito ao veículo original, assinado como "Redação GOLstory". Modelo
   equivalente ao de agregadores como Techmeme/Feedly.
2. **Análise GOLstory** (`workflow-analise-autoral.json`) — coluna de
   opinião/análise **original**, que usa a notícia apenas como gancho
   factual, sempre citando e linkando a(s) fonte(s) no corpo do texto, com
   perspectiva de mercado nova adicionada por Wemerson M. Oliveira (CEO do
   Grupo GOLup). É esse fluxo que fica assinado por ele, porque o texto é de
   fato uma análise autoral, não uma tradução disfarçada.

Se em algum momento o objetivo for republicar o texto quase integral de uma
matéria, isso exige licenciamento/parceria de conteúdo com o veículo — fora
do escopo desta automação.

## Estrutura

```
automations/golstory-ai-radar/
├── sources.json                     # 150 fontes de conhecimento de IA curadas
├── docker/
│   ├── docker-compose.yml           # n8n + Postgres, atrás do Traefik existente
│   ├── .env.example                 # variáveis a preencher (copiar para .env)
│   └── init-db.sql                  # tabela de controle/dedupe
└── n8n/
    ├── workflow-radar-noticias.json     # roda a cada 1h
    └── workflow-analise-autoral.json    # roda a cada 2h (perpétuo)
```

## 1. Fontes (`sources.json`)

150 fontes organizadas por categoria: AI Labs, mídia tech, mídia de IA
dedicada, academia/arXiv, newsletters, analistas/consultorias,
policy/safety, blogs de plataformas/dev tools, imprensa regional
(Ásia/Europa) e imprensa BR/LatAm. Cada entrada tem `tier` (1 = essencial,
2 = importante, 3 = complementar) e `rss` (`null` quando o feed precisa ser
confirmado manualmente ou obtido via [RSS-Bridge](https://github.com/RSS-Bridge/rss-bridge)
antes de ativar a fonte). Os workflows, por padrão, só usam fontes com
`tier` 1 ou 2 **e** `rss` preenchido — edite o filtro no node "Fontes
ativas" para incluir mais fontes conforme for validando os feeds.

## 2. Deploy no VPS Hostinger

Acesse o servidor (IP `187.127.13.69`) via SSH.

```bash
# 1. Confirme o nome da rede externa do Traefik já instalado
docker network ls

# 2. Clone/copie esta pasta para o servidor, ex:
git clone <este-repo> /opt/golstory-ai-radar
cd /opt/golstory-ai-radar/automations/golstory-ai-radar/docker

# 3. Configure o .env
cp .env.example .env
nano .env   # preencha TRAEFIK_NETWORK, TRAEFIK_CERTRESOLVER, N8N_ENCRYPTION_KEY, etc.

# 4. Suba o stack
docker compose up -d
docker compose logs -f n8n
```

Aponte um registro DNS tipo A de `n8n.golstory.com.br` (ou subdomínio de
sua escolha) para `187.127.13.69` antes de subir, para o Traefik conseguir
emitir o certificado TLS.

## 3. WordPress do GOLstory

1. Em `wp-admin → Usuários`, crie (ou use) dois usuários:
   - **Redação GOLstory** — autor dos posts do Radar IA.
   - **Wemerson M. Oliveira** — bio com "CEO do Grupo GOLup"; autor da
     coluna de Análise.
2. Em `wp-admin → Usuários → Perfil → Senhas de Aplicativo`, gere uma senha
   de aplicativo para o usuário que a API vai usar para publicar (precisa
   de permissão de editor/admin). Preencha `WORDPRESS_USER` e
   `WORDPRESS_APP_PASSWORD` no `.env`.
3. Crie duas categorias (`wp-admin → Posts → Categorias`): `Radar IA` e
   `Análise GOLstory`. Preencha os IDs no `.env`.
4. Preencha `WORDPRESS_AUTHOR_ID_REDACAO` e `WORDPRESS_AUTHOR_ID_WEMERSON`
   com o ID numérico de cada usuário (visível na URL ao editar o perfil).

## 4. Importar os workflows no n8n

1. Acesse `https://n8n.<seu-subdominio>`, crie o usuário admin (primeiro
   acesso).
2. Em **Credentials**, crie:
   - `Postgres GOLstory` (host `postgres`, porta `5432`, database
     `golstory`, usuário/senha do `.env`).
   - `WordPress GOLstory` (Basic Auth com `WORDPRESS_USER` +
     `WORDPRESS_APP_PASSWORD`, apontando para `WORDPRESS_URL`).
   - `Anthropic API Key` (Header Auth: nome do header `x-api-key`, valor a
     sua `ANTHROPIC_API_KEY`).
   - `OpenAI API Key` (Header Auth: nome do header `Authorization`, valor
     `Bearer <sua OPENAI_API_KEY>`).
3. Em **Settings → Environment Variables** (ou no `.env` do container),
   defina `WORDPRESS_AUTHOR_ID_REDACAO`, `WORDPRESS_AUTHOR_ID_WEMERSON`,
   `WORDPRESS_CATEGORY_ID_RADAR`, `WORDPRESS_CATEGORY_ID_ANALISE`.
4. Importe `n8n/workflow-radar-noticias.json` e
   `n8n/workflow-analise-autoral.json` (**Workflows → Import from File**).
5. Em cada node de credencial (Postgres, WordPress, HTTP Request com
   `httpHeaderAuth`), reselecione a credencial criada no passo 2 — o import
   não vincula credenciais automaticamente.
6. Rode cada workflow manualmente uma vez ("Execute Workflow") para validar
   antes de ativar (toggle "Active").

## 5. Rate limiting e custo

- **Radar IA**: roda a cada hora, processa só itens publicados na última
  hora nas fontes `tier` 1-2 — volume esperado de poucas dezenas de posts
  curtos por dia.
- **Análise GOLstory**: roda a cada 2h, mas só avança para geração de texto
  + imagem quando a IA pontua a notícia com relevância ≥ 7/10 — evita gerar
  dezenas de colunas de baixa qualidade e mantém custo de API previsível.
  Ajuste o limiar no node "So itens com score >= 7" e o `LIMIT` da query em
  "Selecionar candidatos" conforme o orçamento de API disponível.

## 6. Próximos passos sugeridos

- Validar manualmente os feeds RSS marcados com `"rss": null` em
  `sources.json` (muitos sites exigem RSS-Bridge ou scraping dedicado).
- Adicionar um node de notificação (Slack/e-mail) no branch de erro de cada
  workflow para acompanhar falhas de publicação.
- Revisar periodicamente (manual ou por amostragem) os textos gerados antes
  de manter a publicação 100% automática, para garantir qualidade e
  aderência às regras de atribuição.
