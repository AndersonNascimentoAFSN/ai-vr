# 📊 Modelo de Banco de Dados - Sistema de VR/VA

## 🎯 Visão Geral

Este documento descreve o modelo de banco de dados relacional desenvolvido para automatizar o cálculo de VR (Vale Refeição). O banco foi projetado para armazenar e relacionar todas as informações das planilhas Excel, permitindo consultas eficientes e cálculos automatizados.

## 🏗️ Arquitetura do Banco

### **Tecnologia Utilizada**
- **SGBD**: SQLite (em memória para desenvolvimento)
- **Linguagem**: SQL
- **Interface**: Python com pandas e sqlite3

### **Características Principais**
- ✅ **Normalizado**: Segue as 3 formas normais
- ✅ **Relacional**: Chaves estrangeiras bem definidas
- ✅ **Índices**: Otimizado para consultas frequentes
- ✅ **Views**: Facilita consultas complexas
- ✅ **Triggers**: Manutenção automática de timestamps

## 📋 Estrutura das Tabelas

### **1. Tabelas Principais**

#### **colaboradores** (Tabela Central)
```sql
CREATE TABLE colaboradores (
    id INTEGER PRIMARY KEY,
    matricula INTEGER NOT NULL UNIQUE,
    nome VARCHAR(200),
    empresa_id INTEGER NOT NULL,
    cargo_id INTEGER NOT NULL,
    sindicato_id INTEGER NOT NULL,
    situacao VARCHAR(50) NOT NULL,
    data_admissao DATE,
    data_desligamento DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Propósito**: Armazena todos os colaboradores da empresa
**Chave Primária**: `id`
**Chaves Estrangeiras**: 
- `empresa_id` → `empresas(id)`
- `cargo_id` → `cargos(id)`
- `sindicato_id` → `sindicatos(id)`

#### **sindicatos**
```sql
CREATE TABLE sindicatos (
    id INTEGER PRIMARY KEY,
    nome_completo VARCHAR(200) NOT NULL UNIQUE,
    nome_abreviado VARCHAR(50),
    estado_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Propósito**: Informações dos sindicatos
**Relacionamentos**: `estado_id` → `estados(id)`

#### **estados**
```sql
CREATE TABLE estados (
    id INTEGER PRIMARY KEY,
    nome VARCHAR(50) NOT NULL UNIQUE,
    uf VARCHAR(2) NOT NULL UNIQUE,
    valor_vr_diario DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Propósito**: Estados e seus valores de VR
**Dados**: Paraná (R$ 35,00), Rio de Janeiro (R$ 35,00), Rio Grande do Sul (R$ 35,00), São Paulo (R$ 37,50)

#### **cargos**
```sql
CREATE TABLE cargos (
    id INTEGER PRIMARY KEY,
    titulo VARCHAR(100) NOT NULL,
    categoria VARCHAR(50), -- DIRETOR, ESTAGIARIO, APRENDIZ, FUNCIONARIO
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Propósito**: Cargos dos colaboradores com categorização
**Categorias**: FUNCIONARIO, ESTAGIARIO, APRENDIZ, DIRETOR

#### **empresas**
```sql
CREATE TABLE empresas (
    id INTEGER PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cnpj VARCHAR(18),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Propósito**: Empresas do grupo (atualmente apenas uma)

### **2. Tabelas de Configuração**

#### **dias_uteis**
```sql
CREATE TABLE dias_uteis (
    id INTEGER PRIMARY KEY,
    sindicato_id INTEGER NOT NULL,
    periodo_inicio DATE NOT NULL,
    periodo_fim DATE NOT NULL,
    dias_uteis INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Propósito**: Dias úteis por sindicato e período
**Dados**: PR (22 dias), RS (21 dias), SP (22 dias), RJ (21 dias)

### **3. Tabelas de Relacionamento**

#### **ferias**
```sql
CREATE TABLE ferias (
    id INTEGER PRIMARY KEY,
    colaborador_id INTEGER NOT NULL,
    periodo_inicio DATE NOT NULL,
    periodo_fim DATE NOT NULL,
    dias_ferias INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Propósito**: Relaciona colaboradores com férias
**Relacionamento**: `colaborador_id` → `colaboradores(id)`

#### **afastamentos**
```sql
CREATE TABLE afastamentos (
    id INTEGER PRIMARY KEY,
    colaborador_id INTEGER NOT NULL,
    tipo_afastamento VARCHAR(100) NOT NULL,
    data_inicio DATE NOT NULL,
    data_fim DATE,
    observacoes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Propósito**: Colaboradores afastados (licença maternidade, auxílio doença, etc.)
**Tipos**: Licença Maternidade, Auxílio Doença, Atestado

#### **desligamentos**
```sql
CREATE TABLE desligamentos (
    id INTEGER PRIMARY KEY,
    colaborador_id INTEGER NOT NULL,
    data_desligamento DATE NOT NULL,
    comunicado_ok BOOLEAN DEFAULT FALSE,
    observacoes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Propósito**: Colaboradores desligados com regra de VR
**Regra**: Se `comunicado_ok = TRUE` até dia 15, não recebe VR

#### **admissoes**
```sql
CREATE TABLE admissoes (
    id INTEGER PRIMARY KEY,
    colaborador_id INTEGER NOT NULL,
    data_admissao DATE NOT NULL,
    cargo_id INTEGER NOT NULL,
    observacoes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Propósito**: Novos colaboradores admitidos no mês
**Relacionamento**: `colaborador_id` → `colaboradores(id)`

#### **exclusoes**
```sql
CREATE TABLE exclusoes (
    id INTEGER PRIMARY KEY,
    colaborador_id INTEGER NOT NULL,
    tipo_exclusao VARCHAR(50) NOT NULL, -- ESTAGIARIO, APRENDIZ, EXTERIOR
    valor_especifico DECIMAL(10,2), -- Para colaboradores no exterior
    observacoes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Propósito**: Colaboradores excluídos do VR
**Tipos**: ESTAGIARIO, APRENDIZ, EXTERIOR

### **4. Tabelas de Cálculo**

#### **calculos_vr**
```sql
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Propósito**: Resultados dos cálculos de VR
**Relacionamento**: `colaborador_id` → `colaboradores(id)`

## 🔗 Diagrama de Relacionamentos

```
empresas (1) ←→ (N) colaboradores (N) ←→ (1) sindicatos (N) ←→ (1) estados
     ↑                    ↑                    ↑
     │                    │                    │
     │                    │                    │
cargos (1) ←→ (N) colaboradores (N) ←→ (1) dias_uteis
     ↑                    ↑
     │                    │
     │                    ├── ferias (1:N)
     │                    ├── afastamentos (1:N)
     │                    ├── desligamentos (1:N)
     │                    ├── admissoes (1:N)
     │                    └── exclusoes (1:N)
     │
     └── calculos_vr (1:N)
```

## 📊 Views Criadas

### **colaboradores_elegiveis**
```sql
CREATE VIEW colaboradores_elegiveis AS
SELECT 
    c.id, c.matricula, c.nome, c.situacao,
    c.data_admissao, c.data_desligamento,
    emp.nome as empresa, car.titulo as cargo,
    car.categoria as categoria_cargo,
    s.nome_completo as sindicato,
    e.nome as estado, e.valor_vr_diario
FROM colaboradores c
JOIN empresas emp ON c.empresa_id = emp.id
JOIN cargos car ON c.cargo_id = car.id
JOIN sindicatos s ON c.sindicato_id = s.id
JOIN estados e ON s.estado_id = e.id
WHERE c.id NOT IN (SELECT colaborador_id FROM exclusoes)
AND c.situacao NOT IN ('Auxílio Doença', 'Licença Maternidade', 'Atestado');
```

**Propósito**: Colaboradores elegíveis para receber VR

### **resumo_calculos_vr**
```sql
CREATE VIEW resumo_calculos_vr AS
SELECT 
    periodo_mes, periodo_ano,
    COUNT(*) as total_colaboradores,
    SUM(dias_vr_calculados) as total_dias_vr,
    SUM(valor_total) as valor_total_vr,
    SUM(custo_empresa) as custo_total_empresa,
    SUM(desconto_colaborador) as desconto_total_colaborador
FROM calculos_vr
GROUP BY periodo_mes, periodo_ano;
```

**Propósito**: Resumo dos cálculos por período

## 🔍 Índices Criados

```sql
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
```

## ⚙️ Triggers

### **update_colaboradores_timestamp**
```sql
CREATE TRIGGER update_colaboradores_timestamp 
    AFTER UPDATE ON colaboradores
    FOR EACH ROW
BEGIN
    UPDATE colaboradores SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
```

**Propósito**: Atualiza automaticamente o campo `updated_at`

## 📈 Estatísticas do Banco

### **Dados Populados**
- **Colaboradores**: 1.815 ativos
- **Sindicatos**: 4 (PR, RS, SP, RJ)
- **Estados**: 4 com valores de VR
- **Cargos**: 170 diferentes categorizados
- **Férias**: 80 colaboradores
- **Afastamentos**: 20 colaboradores
- **Desligamentos**: 51 colaboradores
- **Admissões**: 83 novos colaboradores
- **Exclusões**: 64 (27 estagiários + 33 aprendizes + 4 exterior)

## 🚀 Como Usar

### **1. Criar e Popular o Banco**
```python
from database_populate import VRDatabase

# Criar banco em memória
db = VRDatabase(":memory:")
db.populate_all()

# Ver estatísticas
stats = db.get_stats()
print(stats)
```

### **2. Executar Consultas**
```python
from database_queries import VRQueries

# Executar consultas de exemplo
queries = VRQueries()
queries.run_all_queries()
```

### **3. Consultas Personalizadas**
```python
import pandas as pd

# Exemplo: Colaboradores elegíveis para VR
query = """
SELECT c.matricula, car.titulo, s.nome_abreviado, e.valor_vr_diario
FROM colaboradores c
JOIN cargos car ON c.cargo_id = car.id
JOIN sindicatos s ON c.sindicato_id = s.id
JOIN estados e ON s.estado_id = e.id
WHERE c.id NOT IN (SELECT colaborador_id FROM exclusoes)
AND car.categoria = 'FUNCIONARIO'
"""

df = pd.read_sql_query(query, db.conn)
print(df)
```

## ✅ Validações Implementadas

### **1. Integridade Referencial**
- Todas as chaves estrangeiras estão definidas
- `PRAGMA foreign_keys = ON` ativado

### **2. Unicidade**
- Matrícula única por colaborador
- Nomes únicos para sindicatos e estados
- Cálculo único por colaborador/período

### **3. Consistência de Dados**
- Validação de tipos de dados
- Constraints de NOT NULL onde necessário
- Valores padrão apropriados

## 🔧 Manutenção

### **Backup e Restore**
```python
# Backup
import sqlite3
conn = sqlite3.connect('vr_database.db')
with open('backup.sql', 'w') as f:
    for line in conn.iterdump():
        f.write('%s\n' % line)

# Restore
conn = sqlite3.connect(':memory:')
with open('backup.sql', 'r') as f:
    conn.executescript(f.read())
```

### **Limpeza de Dados**
```sql
-- Limpar cálculos antigos
DELETE FROM calculos_vr WHERE periodo_ano < 2025;

-- Limpar férias antigas
DELETE FROM ferias WHERE periodo_fim < '2025-01-01';
```

## 📋 Próximos Passos

1. **Implementar algoritmo de cálculo** usando as tabelas criadas
2. **Criar interface de usuário** para visualização dos dados
3. **Implementar validações** de negócio no banco
4. **Criar relatórios** baseados nas views
5. **Implementar auditoria** de mudanças
6. **Otimizar performance** para grandes volumes

---

**Nota**: Este modelo de banco de dados foi projetado especificamente para o sistema de VR/VA, considerando todas as regras de negócio documentadas e os dados das planilhas Excel fornecidas.
