-- =====================================================
-- SCHEMA DO BANCO DE DADOS - SISTEMA DE VR/VA
-- =====================================================

-- Configurações
PRAGMA foreign_keys = ON;

-- =====================================================
-- TABELAS PRINCIPAIS
-- =====================================================

-- Tabela de empresas
CREATE TABLE empresas (
    id INTEGER PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cnpj VARCHAR(18),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de estados
CREATE TABLE estados (
    id INTEGER PRIMARY KEY,
    nome VARCHAR(50) NOT NULL UNIQUE,
    uf VARCHAR(2) NOT NULL UNIQUE,
    valor_vr_diario DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de sindicatos
CREATE TABLE sindicatos (
    id INTEGER PRIMARY KEY,
    nome_completo VARCHAR(200) NOT NULL UNIQUE,
    nome_abreviado VARCHAR(50),
    estado_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (estado_id) REFERENCES estados(id)
);

-- Tabela de cargos
CREATE TABLE cargos (
    id INTEGER PRIMARY KEY,
    titulo VARCHAR(100) NOT NULL,
    categoria VARCHAR(50), -- DIRETOR, ESTAGIARIO, APRENDIZ, FUNCIONARIO
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela principal de colaboradores
CREATE TABLE colaboradores (
    id INTEGER PRIMARY KEY,
    matricula INTEGER NOT NULL UNIQUE,
    nome VARCHAR(200),
    empresa_id INTEGER NOT NULL,
    cargo_id INTEGER NOT NULL,
    sindicato_id INTEGER NOT NULL,
    situacao VARCHAR(50) NOT NULL, -- Trabalhando, Férias, Atestado, Auxílio Doença, Licença Maternidade
    data_admissao DATE,
    data_desligamento DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (empresa_id) REFERENCES empresas(id),
    FOREIGN KEY (cargo_id) REFERENCES cargos(id),
    FOREIGN KEY (sindicato_id) REFERENCES sindicatos(id)
);

-- =====================================================
-- TABELAS DE CONFIGURAÇÃO
-- =====================================================

-- Tabela de dias úteis por sindicato e período
CREATE TABLE dias_uteis (
    id INTEGER PRIMARY KEY,
    sindicato_id INTEGER NOT NULL,
    periodo_inicio DATE NOT NULL,
    periodo_fim DATE NOT NULL,
    dias_uteis INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sindicato_id) REFERENCES sindicatos(id),
    UNIQUE(sindicato_id, periodo_inicio, periodo_fim)
);

-- =====================================================
-- TABELAS DE RELACIONAMENTO
-- =====================================================

-- Tabela de férias
CREATE TABLE ferias (
    id INTEGER PRIMARY KEY,
    colaborador_id INTEGER NOT NULL,
    periodo_inicio DATE NOT NULL,
    periodo_fim DATE NOT NULL,
    dias_ferias INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (colaborador_id) REFERENCES colaboradores(id)
);

-- Tabela de afastamentos
CREATE TABLE afastamentos (
    id INTEGER PRIMARY KEY,
    colaborador_id INTEGER NOT NULL,
    tipo_afastamento VARCHAR(100) NOT NULL, -- Licença Maternidade, Auxílio Doença, etc.
    data_inicio DATE NOT NULL,
    data_fim DATE,
    observacoes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (colaborador_id) REFERENCES colaboradores(id)
);

-- Tabela de desligamentos
CREATE TABLE desligamentos (
    id INTEGER PRIMARY KEY,
    colaborador_id INTEGER NOT NULL,
    data_desligamento DATE NOT NULL,
    comunicado_ok BOOLEAN DEFAULT FALSE,
    observacoes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (colaborador_id) REFERENCES colaboradores(id)
);

-- Tabela de admissões (novos colaboradores)
CREATE TABLE admissoes (
    id INTEGER PRIMARY KEY,
    colaborador_id INTEGER NOT NULL,
    data_admissao DATE NOT NULL,
    cargo_id INTEGER NOT NULL,
    observacoes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (colaborador_id) REFERENCES colaboradores(id),
    FOREIGN KEY (cargo_id) REFERENCES cargos(id)
);

-- Tabela de exclusões (estagiários, aprendizes, exterior)
CREATE TABLE exclusoes (
    id INTEGER PRIMARY KEY,
    colaborador_id INTEGER NOT NULL,
    tipo_exclusao VARCHAR(50) NOT NULL, -- ESTAGIARIO, APRENDIZ, EXTERIOR
    valor_especifico DECIMAL(10,2), -- Para colaboradores no exterior
    observacoes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (colaborador_id) REFERENCES colaboradores(id)
);

-- =====================================================
-- TABELAS DE CÁLCULO E RESULTADO
-- =====================================================

-- Tabela de cálculos de VR
CREATE TABLE calculos_vr (
    id INTEGER PRIMARY KEY,
    colaborador_id INTEGER NOT NULL,
    periodo_mes INTEGER NOT NULL, -- 1-12
    periodo_ano INTEGER NOT NULL,
    dias_uteis_sindicato INTEGER NOT NULL,
    dias_ferias INTEGER DEFAULT 0,
    dias_trabalhados INTEGER NOT NULL,
    dias_vr_calculados INTEGER NOT NULL,
    valor_diario DECIMAL(10,2) NOT NULL,
    valor_total DECIMAL(10,2) NOT NULL,
    custo_empresa DECIMAL(10,2) NOT NULL,
    desconto_colaborador DECIMAL(10,2) NOT NULL,
    observacoes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (colaborador_id) REFERENCES colaboradores(id),
    UNIQUE(colaborador_id, periodo_mes, periodo_ano)
);

-- =====================================================
-- ÍNDICES PARA PERFORMANCE
-- =====================================================

-- Índices para consultas frequentes
CREATE INDEX idx_colaboradores_matricula ON colaboradores(matricula);
CREATE INDEX idx_colaboradores_situacao ON colaboradores(situacao);
CREATE INDEX idx_colaboradores_sindicato ON colaboradores(sindicato_id);
CREATE INDEX idx_ferias_colaborador ON ferias(colaborador_id);
CREATE INDEX idx_afastamentos_colaborador ON afastamentos(colaborador_id);
CREATE INDEX idx_desligamentos_colaborador ON desligamentos(colaborador_id);
CREATE INDEX idx_exclusoes_colaborador ON exclusoes(colaborador_id);
CREATE INDEX idx_calculos_vr_colaborador ON calculos_vr(colaborador_id);
CREATE INDEX idx_calculos_vr_periodo ON calculos_vr(periodo_mes, periodo_ano);

-- =====================================================
-- VIEWS PARA FACILITAR CONSULTAS
-- =====================================================

-- View para colaboradores elegíveis para VR
CREATE VIEW colaboradores_elegiveis AS
SELECT 
    c.id,
    c.matricula,
    c.nome,
    c.situacao,
    c.data_admissao,
    c.data_desligamento,
    emp.nome as empresa,
    car.titulo as cargo,
    car.categoria as categoria_cargo,
    s.nome_completo as sindicato,
    e.nome as estado,
    e.valor_vr_diario
FROM colaboradores c
JOIN empresas emp ON c.empresa_id = emp.id
JOIN cargos car ON c.cargo_id = car.id
JOIN sindicatos s ON c.sindicato_id = s.id
JOIN estados e ON s.estado_id = e.id
WHERE c.id NOT IN (
    SELECT colaborador_id FROM exclusoes
)
AND c.situacao NOT IN ('Auxílio Doença', 'Licença Maternidade', 'Atestado');

-- View para resumo de cálculos por período
CREATE VIEW resumo_calculos_vr AS
SELECT 
    periodo_mes,
    periodo_ano,
    COUNT(*) as total_colaboradores,
    SUM(dias_vr_calculados) as total_dias_vr,
    SUM(valor_total) as valor_total_vr,
    SUM(custo_empresa) as custo_total_empresa,
    SUM(desconto_colaborador) as desconto_total_colaborador
FROM calculos_vr
GROUP BY periodo_mes, periodo_ano;

-- =====================================================
-- TRIGGERS PARA MANUTENÇÃO
-- =====================================================

-- Trigger para atualizar updated_at
CREATE TRIGGER update_colaboradores_timestamp 
    AFTER UPDATE ON colaboradores
    FOR EACH ROW
BEGIN
    UPDATE colaboradores SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
