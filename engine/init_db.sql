-- economies table: 80 major nations
CREATE TABLE IF NOT EXISTS economies (
    id VARCHAR(5) PRIMARY KEY, -- ISO Code (e.g., USA, CHN, SGP)
    name VARCHAR(100) NOT NULL,
    gdp_usd_bn NUMERIC(15, 2) NOT NULL, -- GDP in Billions USD
    last_updated DATE DEFAULT CURRENT_DATE
);

-- industries table: 50 sectors (ISIC Rev. 4)
CREATE TABLE IF NOT EXISTS industries (
    id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    category VARCHAR(50) -- e.g., Primary, Manufacturing, Services
);

-- trade_matrix table: 4,000+ nodes (80 economies * 50 sectors)
-- Captures the "Value Added" from Source Economy -> Target Economy for a specific Industry
CREATE TABLE IF NOT EXISTS trade_matrix (
    id SERIAL PRIMARY KEY,
    source_econ_id VARCHAR(5) REFERENCES economies(id),
    target_econ_id VARCHAR(5) REFERENCES economies(id),
    industry_id VARCHAR(10) REFERENCES industries(id),
    value_added_usd_mn NUMERIC(15, 2) NOT NULL, -- Value Added in Millions USD
    UNIQUE(source_econ_id, target_econ_id, industry_id)
);

-- Indices for performance on recursive queries
CREATE INDEX IF NOT EXISTS idx_trade_matrix_source ON trade_matrix(source_econ_id);
CREATE INDEX IF NOT EXISTS idx_trade_matrix_target ON trade_matrix(target_econ_id);
CREATE INDEX IF NOT EXISTS idx_trade_matrix_industry ON trade_matrix(industry_id);
