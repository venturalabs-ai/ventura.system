# Instrucoes para o Agente de IA da Hostinger (hpanel.hostinger.com/agent)

Copie e cole o bloco abaixo na conversa com o agente da Hostinger. Ele foi
escrito para ser executado passo a passo, com pontos claros onde o agente
deve PARAR e pedir informacoes/segredos ao usuario em vez de inventa-los.

---

## Prompt para colar no agente

```
Voce vai configurar uma automacao de conteudo (n8n) no meu VPS Hostinger
para o site GOLstory.com.br. Servidor: srv1925412.hstgr.cloud (Ubuntu 24.04,
ja com Docker e Traefik instalados), IP 187.127.13.69.

Os arquivos de configuracao (docker-compose.yml, .env.example, init-db.sql,
sources.json e os dois workflows n8n) estao neste repositorio GitHub:
https://github.com/venturalabs-ai/ventura.system
pasta: automations/golstory-ai-radar/
branch: claude/n8n-ai-golstory-routine-qa889c (ou "main" se o PR #9 ja
tiver sido mesclado - confira antes de clonar).

Siga estes passos NA ORDEM, via SSH no VPS:

1. Verifique a rede Docker do Traefik ja existente:
   docker network ls
   Anote o nome da rede que o Traefik usa (geralmente algo como
   "traefik_default" ou "traefik-public").

2. Clone o repositorio no servidor:
   git clone -b claude/n8n-ai-golstory-routine-qa889c \
     https://github.com/venturalabs-ai/ventura.system.git /opt/golstory-ai-radar
   cd /opt/golstory-ai-radar/automations/golstory-ai-radar/docker

3. Copie o arquivo de exemplo de variaveis de ambiente:
   cp .env.example .env

4. PARE AQUI e me pergunte, um de cada vez, os seguintes valores (NAO
   invente nenhum deles, NAO gere senha de aplicativo do WordPress sozinho
   - eu preciso gerar manualmente no wp-admin):
   - TRAEFIK_NETWORK (nome da rede identificado no passo 1)
   - TRAEFIK_CERTRESOLVER (nome do certresolver configurado no Traefik;
     se eu nao souber, verifique nos labels do container do Traefik com
     "docker inspect" e me mostre as opcoes)
   - N8N_ENCRYPTION_KEY (gere voce mesmo com: openssl rand -hex 32)
   - POSTGRES_PASSWORD (gere voce mesmo com: openssl rand -hex 20)
   - WORDPRESS_URL (provavelmente https://golstory.com.br, confirme comigo)
   - WORDPRESS_USER e WORDPRESS_APP_PASSWORD (eu vou gerar em
     wp-admin -> Usuarios -> Perfil -> Senhas de Aplicativo e te enviar)
   - WORDPRESS_AUTHOR_ID_REDACAO e WORDPRESS_AUTHOR_ID_WEMERSON (IDs dos
     dois usuarios do WordPress - "Redacao GOLstory" e "Wemerson M.
     Oliveira"; se ainda nao existirem, me avise para eu criar antes)
   - WORDPRESS_CATEGORY_ID_RADAR e WORDPRESS_CATEGORY_ID_ANALISE (IDs das
     categorias "Radar IA" e "Analise GOLstory" no WordPress)
   - ANTHROPIC_API_KEY (chave da API da Anthropic para geracao de texto)
   - OPENAI_API_KEY (chave da API da OpenAI para geracao de imagem de capa)

   Preencha o arquivo .env com esses valores (edite com nano ou vim).

5. Configure o DNS: crie um registro tipo A apontando
   n8n.golstory.com.br -> 187.127.13.69
   (isso e feito no painel de DNS do dominio, nao no VPS - se voce tiver
   acesso ao DNS da Hostinger para este dominio, faca voce mesmo e me avise
   quando propagar; senao me diga exatamente o registro que preciso criar).

6. Suba os containers:
   docker compose up -d
   docker compose logs -f n8n
   Confirme que o Traefik emitiu certificado TLS e que
   https://n8n.golstory.com.br carrega a tela de setup do n8n.

7. Me avise quando concluir os passos 1-6. Os proximos passos (criar
   usuario admin do n8n, cadastrar credenciais, importar os dois
   workflows JSON, configurar categorias/autores no WordPress) exigem
   interacao manual minha na interface do n8n e do wp-admin - nao tente
   automatizar login em nenhuma dessas interfaces.

Regras gerais:
- Nunca invente chave de API, senha ou ID que eu nao tenha te passado.
- Nunca publique ou ative os workflows n8n sozinho - eles ficam com
  "active: false" ate eu revisar manualmente uma execucao de teste.
- Se qualquer comando falhar, me mostre o erro completo antes de tentar
  outra abordagem.
```

---

## O que fazer depois que o agente terminar os passos acima

Isso cobre só a parte de infraestrutura (subir n8n + Postgres no VPS). Os
passos manuais finais — criar credenciais no n8n, importar os workflows e
configurar usuários/categorias no WordPress — estão detalhados no
[`README.md`](./README.md) desta mesma pasta, seções 3 e 4. Volte a este
projeto (Claude Code) se quiser ajuda para revisar a primeira execução de
teste de cada workflow antes de ativá-los.
