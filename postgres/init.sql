-- Criar o banco de dados apenas se não existir
DO $$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_database WHERE datname = 'brain_agro'
   ) THEN
      CREATE DATABASE brain_agro;
   END IF;
END
$$;

-- Conectar ao banco de dados brain_agro
\connect brain_agro;

-- Mensagem para depuração
DO $$ BEGIN RAISE NOTICE 'Conectado ao banco de dados brain_agro'; END $$;

-- Criação das tabelas de culturas
CREATE TABLE IF NOT EXISTS arroz (
    id SERIAL PRIMARY KEY,
    localidade VARCHAR(10),
    unidade VARCHAR(20),
    jan NUMERIC(10, 2),
    fev NUMERIC(10, 2),
    mar NUMERIC(10, 2),
    abr NUMERIC(10, 2),
    mai NUMERIC(10, 2),
    jun NUMERIC(10, 2),
    jul NUMERIC(10, 2),
    ago NUMERIC(10, 2),
    set NUMERIC(10, 2),
    out NUMERIC(10, 2),
    nov NUMERIC(10, 2),
    dez NUMERIC(10, 2)
);

CREATE TABLE IF NOT EXISTS milho (
    id SERIAL PRIMARY KEY,
    localidade VARCHAR(10),
    unidade VARCHAR(20),
    jan NUMERIC(10, 2),
    fev NUMERIC(10, 2),
    mar NUMERIC(10, 2),
    abr NUMERIC(10, 2),
    mai NUMERIC(10, 2),
    jun NUMERIC(10, 2),
    jul NUMERIC(10, 2),
    ago NUMERIC(10, 2),
    set NUMERIC(10, 2),
    out NUMERIC(10, 2),
    nov NUMERIC(10, 2),
    dez NUMERIC(10, 2)
);

CREATE TABLE IF NOT EXISTS soja (
    id SERIAL PRIMARY KEY,
    localidade VARCHAR(10),
    unidade VARCHAR(20),
    jan NUMERIC(10, 2),
    fev NUMERIC(10, 2),
    mar NUMERIC(10, 2),
    abr NUMERIC(10, 2),
    mai NUMERIC(10, 2),
    jun NUMERIC(10, 2),
    jul NUMERIC(10, 2),
    ago NUMERIC(10, 2),
    set NUMERIC(10, 2),
    out NUMERIC(10, 2),
    nov NUMERIC(10, 2),
    dez NUMERIC(10, 2)
);

CREATE TABLE IF NOT EXISTS trigo (
    id SERIAL PRIMARY KEY,
    localidade VARCHAR(10),
    unidade VARCHAR(20),
    jan NUMERIC(10, 2),
    fev NUMERIC(10, 2),
    mar NUMERIC(10, 2),
    abr NUMERIC(10, 2),
    mai NUMERIC(10, 2),
    jun NUMERIC(10, 2),
    jul NUMERIC(10, 2),
    ago NUMERIC(10, 2),
    set NUMERIC(10, 2),
    out NUMERIC(10, 2),
    nov NUMERIC(10, 2),
    dez NUMERIC(10, 2)
);

-- Criação da tabela de fertilizantes
CREATE TABLE IF NOT EXISTS fertilizantes (
    id SERIAL PRIMARY KEY,
    unidade_federacao VARCHAR(2),
    municipio VARCHAR(50),
    numero_registro VARCHAR(20),
    status_registro VARCHAR(10),
    cnpj VARCHAR(20),
    razao_social VARCHAR(200),
    nome_fantasia VARCHAR(200),
    area_atuacao VARCHAR(50),
    atividade VARCHAR(50),
    classificacao VARCHAR(200)
);


CREATE TABLE IF NOT EXISTS declaracao_producao (
    id SERIAL PRIMARY KEY,
    tipo_periodo VARCHAR(20),
    periodo VARCHAR(20),
    area_total NUMERIC(10, 2),
    municipio VARCHAR(50),
    uf VARCHAR(2),
    especie VARCHAR(50),
    cultivar VARCHAR(50),
    area_plantada NUMERIC(10, 2),
    area_estimada NUMERIC(10, 2),
    quant_reservada NUMERIC(10, 2),
    data_plantio TIMESTAMP
);
CREATE TABLE IF NOT EXISTS producao_semente (
    id SERIAL PRIMARY KEY,
    safra VARCHAR(20),
    especie VARCHAR(50),
    categoria VARCHAR(20),
    cultivar VARCHAR(50),
    municipio VARCHAR(50),
    uf VARCHAR(2),
    status VARCHAR(20),
    data_plantio DATE,
    data_colheita DATE,
    area NUMERIC(10, 2),
    producao_bruta NUMERIC(10, 2),
    producao_estimada NUMERIC(10, 2)
);
CREATE TABLE IF NOT EXISTS semente (
    id SERIAL PRIMARY KEY,
    produto VARCHAR(100),
    unidade VARCHAR(10),
    uf VARCHAR(2),
    ano INTEGER,
    jan NUMERIC(10, 2),
    fev NUMERIC(10, 2),
    mar NUMERIC(10, 2),
    abr NUMERIC(10, 2),
    mai NUMERIC(10, 2),
    jun NUMERIC(10, 2),
    jul NUMERIC(10, 2),
    ago NUMERIC(10, 2),
    set NUMERIC(10, 2),
    out NUMERIC(10, 2),
    nov NUMERIC(10, 2),
    dez NUMERIC(10, 2)
);

CREATE TABLE IF NOT EXISTS producao_fertilizantes (
    id SERIAL PRIMARY KEY,
    produto VARCHAR(100),
    unidade VARCHAR(20),
    uf VARCHAR(2),
    ano INTEGER,
    jan NUMERIC(10, 2),
    fev NUMERIC(10, 2),
    mar NUMERIC(10, 2),
    abr NUMERIC(10, 2),
    mai NUMERIC(10, 2),
    jun NUMERIC(10, 2),
    jul NUMERIC(10, 2),
    ago NUMERIC(10, 2),
    set NUMERIC(10, 2),
    out NUMERIC(10, 2),
    nov NUMERIC(10, 2),
    dez NUMERIC(10, 2)
);
CREATE TABLE IF NOT EXISTS agrotoxico (
    id SERIAL PRIMARY KEY,
    produto VARCHAR(255),
    unidade VARCHAR(20),
    uf VARCHAR(2),
    ano INTEGER,
    jan NUMERIC(10, 2),
    fev NUMERIC(10, 2),
    mar NUMERIC(10, 2),
    abr NUMERIC(10, 2),
    mai NUMERIC(10, 2),
    jun NUMERIC(10, 2),
    jul NUMERIC(10, 2),
    ago NUMERIC(10, 2),
    set NUMERIC(10, 2),
    out NUMERIC(10, 2),
    nov NUMERIC(10, 2),
    dez NUMERIC(10, 2)
);

CREATE TABLE IF NOT EXISTS registro_agrotoxico (
    id SERIAL PRIMARY KEY,
    nr_registro INTEGER,
    marca_comercial VARCHAR(255),
    formulacao VARCHAR(255),
    ingrediente_ativo VARCHAR(255),
    titular_de_registro VARCHAR(255),
    classe VARCHAR(100),
    modo_de_acao VARCHAR(100),
    cultura VARCHAR(255),
    praga_nome_cientifico VARCHAR(255),
    praga_nome_comum VARCHAR(255),
    empresa_pais_tipo TEXT,
    classe_toxicologica VARCHAR(100),
    classe_ambiental VARCHAR(100),
    organicos VARCHAR(10),
    situacao VARCHAR(10)
);
CREATE TABLE IF NOT EXISTS tabua_de_risco (
    nome_cultura VARCHAR(500),          -- Nome da cultura zoneada
    safra_ini INT,                      -- Ano inicial da Safra
    safra_fin INT,                      -- Ano final da Safra
    cod_cultura VARCHAR(500),            -- Código da cultura zoneada
    cod_ciclo VARCHAR(500),              -- Código do ciclo
    cod_solo VARCHAR(500),               -- Código do Solo
    geocodigo VARCHAR(500),              -- Geocódigo do município no IBGE
    uf CHAR(2),                         -- Sigla da Unidade Federativa do município
    municipio VARCHAR(500),             -- Nome do município
    cod_outros_manejos VARCHAR(500),     -- Código dos Tipos de Manejo
    nome_outros_manejos VARCHAR(500),   -- Nome dos Tipos de Manejo
    cod_clima VARCHAR(500),              -- Código do Clima
    nome_clima VARCHAR(500),            -- Nome do Clima
    cod_munic VARCHAR(500),              -- Código do município no Bacen
    cod_meso VARCHAR(500),               -- Código da mesorregião do município no IBGE
    cod_micro VARCHAR(500),              -- Código da microrregião do município do IBGE
    portaria VARCHAR(500),              -- Número e data da portaria de publicação de Zarc no D.O.U.
    dec1 NUMERIC(10, 2) DEFAULT 0,      -- Decêndio 1
    dec2 NUMERIC(10, 2) DEFAULT 0,      -- Decêndio 2
    dec3 NUMERIC(10, 2) DEFAULT 0,      -- Decêndio 3
    dec4 NUMERIC(10, 2) DEFAULT 0,      -- Decêndio 4
    dec5 NUMERIC(10, 2) DEFAULT 0,      -- Decêndio 5
    dec6 NUMERIC(10, 2) DEFAULT 0,      -- Decêndio 6
    dec7 NUMERIC(10, 2) DEFAULT 0,      -- Decêndio 7
    dec8 NUMERIC(10, 2) DEFAULT 0,      -- Decêndio 8
    dec9 NUMERIC(10, 2) DEFAULT 0,      -- Decêndio 9
    dec10 NUMERIC(10, 2) DEFAULT 0,     -- Decêndio 10
    dec11 NUMERIC(10, 2) DEFAULT 0,     -- Decêndio 11
    dec12 NUMERIC(10, 2) DEFAULT 0,     -- Decêndio 12
    dec13 NUMERIC(10, 2) DEFAULT 0,     -- Decêndio 13
    dec14 NUMERIC(10, 2) DEFAULT 0,     -- Decêndio 14
    dec15 NUMERIC(10, 2) DEFAULT 0,     -- Decêndio 15
    dec16 NUMERIC(10, 2) DEFAULT 0,     -- Decêndio 16
    dec17 NUMERIC(10, 2) DEFAULT 0,     -- Decêndio 17
    dec18 NUMERIC(10, 2) DEFAULT 0,     -- Decêndio 18
    dec19 NUMERIC(10, 2) DEFAULT 0,     -- Decêndio 19
    dec20 NUMERIC(10, 2) DEFAULT 0,     -- Decêndio 20
    dec21 NUMERIC(10, 2) DEFAULT 0,     -- Decêndio 21
    dec22 NUMERIC(10, 2) DEFAULT 0,     -- Decêndio 22
    dec23 NUMERIC(10, 2) DEFAULT 0,     -- Decêndio 23
    dec24 NUMERIC(10, 2) DEFAULT 0,     -- Decêndio 24
    dec25 NUMERIC(10, 2) DEFAULT 0,     -- Decêndio 25
    dec26 NUMERIC(10, 2) DEFAULT 0,     -- Decêndio 26
    dec27 NUMERIC(10, 2) DEFAULT 0,     -- Decêndio 27
    dec28 NUMERIC(10, 2) DEFAULT 0,     -- Decêndio 28
    dec29 NUMERIC(10, 2) DEFAULT 0,     -- Decêndio 29
    dec30 NUMERIC(10, 2) DEFAULT 0,     -- Decêndio 30
    dec31 NUMERIC(10, 2) DEFAULT 0,     -- Decêndio 31
    dec32 NUMERIC(10, 2) DEFAULT 0,     -- Decêndio 32
    dec33 NUMERIC(10, 2) DEFAULT 0,     -- Decêndio 33
    dec34 NUMERIC(10, 2) DEFAULT 0,     -- Decêndio 34
    dec35 NUMERIC(10, 2) DEFAULT 0,     -- Decêndio 35
    dec36 NUMERIC(10, 2) DEFAULT 0      -- Decêndio 36
);

ALTER TABLE registro_agrotoxico ALTER COLUMN marca_comercial TYPE VARCHAR(1000);
ALTER TABLE declaracao_producao ALTER COLUMN especie TYPE VARCHAR(200);
-- Mensagem para depuração
DO $$ BEGIN RAISE NOTICE 'Tabelas criadas com sucesso'; END $$;

