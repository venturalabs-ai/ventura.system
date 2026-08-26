-- Tabela de controle usada pelos dois workflows n8n do GOLstory AI Radar.
-- Evita publicar a mesma materia duas vezes e marca quais itens ja viraram
-- coluna de analise autoral.

CREATE TABLE IF NOT EXISTS ai_news_items (
    id              BIGSERIAL PRIMARY KEY,
    source_id       INTEGER NOT NULL,
    source_name     TEXT NOT NULL,
    original_url    TEXT NOT NULL UNIQUE,
    original_title  TEXT NOT NULL,
    published_at    TIMESTAMPTZ,
    fetched_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- Secao "Radar IA" (resumo + atribuicao)
    radar_status        TEXT NOT NULL DEFAULT 'pending', -- pending | published | skipped | error
    radar_wp_post_id    BIGINT,
    radar_published_at  TIMESTAMPTZ,

    -- Secao "Analise GOLstory" (coluna autoral assinada)
    relevance_score      SMALLINT,          -- 0-10, definido por IA
    analise_status        TEXT NOT NULL DEFAULT 'not_selected', -- not_selected | pending | published | skipped | error
    analise_wp_post_id    BIGINT,
    analise_published_at  TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_ai_news_items_radar_status ON ai_news_items (radar_status);
CREATE INDEX IF NOT EXISTS idx_ai_news_items_analise_status ON ai_news_items (analise_status);
CREATE INDEX IF NOT EXISTS idx_ai_news_items_published_at ON ai_news_items (published_at);
