# 🗄️ Banco de Dados SQLite3 - Sistema VR/VA

## 📋 Visão Geral

 Este diretório contém todos os arquivos necessários para criar, gerenciar e consultar o banco de dados SQLite3 do sistema de VR/VA. O banco foi projetado para armazenar todas as informações das planilhas Excel e permitir consultas eficientes para o cálculo automatizado de VR. O script `demo_sistema.py` foi movido para o diretório `ai_vr/scripts` para melhor organização.

## 📁 Arquivos do Sistema

### **Arquivos Principais**
### **Arquivos de Desenvolvimento**
- **`database_populate.py`** - Script original para população (memória)
## 🚀 Como Usar

### **1. Criar o Banco de Dados**

```bash
# Criar e popular o banco de dados
python3 create_database.py
```

**O que acontece:**
- ✅ Cria o arquivo `vr_database.db`
- ✅ Cria todas as tabelas do schema
- ✅ Popula com dados das planilhas Excel
- ✅ Mostra estatísticas do banco

**Saída esperada:**
```
🗄️ SISTEMA DE BANCO DE DADOS VR/VA
============================================================
🗄️ Criando banco de dados: vr_database.db
✅ Banco de dados criado com sucesso!
📋 Criando schema do banco...
✅ Schema criado com sucesso
🏛️ Populando estados...
✅ Estados populados
...
✅ Banco de dados populado com sucesso!

📊 ESTATÍSTICAS DO BANCO:
----------------------------------------
  colaboradores: 1,815 registros
  sindicatos: 4 registros
  estados: 4 registros
  cargos: 188 registros
  empresas: 1 registros
  ferias: 76 registros
  afastamentos: 20 registros
  desligamentos: 3 registros
  admissoes: 73 registros
  exclusoes: 64 registros
  dias_uteis: 4 registros

💾 Banco de dados salvo em: vr_database.db
📏 Tamanho do arquivo: 2,048,000 bytes
```

### **2. Consultar o Banco de Dados**

```bash
# Executar consultas de exemplo
python3 database_connect.py
```

**O que acontece:**
- ✅ Conecta ao banco existente
- ✅ Mostra informações do banco
- ✅ Executa consultas de exemplo
- ✅ Exibe resultados formatados

**Consultas incluídas:**
- 📊 Informações do banco de dados
- 📈 Estatísticas gerais
- 📊 Resumo por sindicato
- 👥 Colaboradores elegíveis para VR
- 🏖️ Colaboradores em férias
- ❌ Colaboradores excluídos
- 💰 Exemplos de cálculo de VR

### **3. Sistema de Backup**

```bash
# Criar backup completo
python3 database_backup.py --backup

# Criar backup apenas do schema
python3 database_backup.py --backup --schema-only

# Listar backups disponíveis
python3 database_backup.py --list

# Restaurar backup
python3 database_backup.py --restore backups/vr_database_backup_20250101_120000.zip

# Limpar backups antigos (mais de 30 dias)
python3 database_backup.py --cleanup 30
```

## 📊 Estrutura do Banco

### **Tabelas Principais**
- **`colaboradores`** - 1.815 colaboradores ativos
- **`sindicatos`** - 4 sindicatos (PR, RS, SP, RJ)
- **`estados`** - 4 estados com valores de VR
- **`cargos`** - 188 cargos categorizados
- **`empresas`** - 1 empresa

### **Tabelas de Relacionamento**
- **`ferias`** - 76 colaboradores em férias
- **`afastamentos`** - 20 colaboradores afastados
- **`desligamentos`** - 3 colaboradores desligados
- **`admissoes`** - 73 novos colaboradores
- **`exclusoes`** - 64 colaboradores excluídos

### **Tabelas de Configuração**
- **`dias_uteis`** - Dias úteis por sindicato e período

## 🔍 Exemplos de Consultas

### **Colaboradores Elegíveis para VR**
```sql
SELECT 
    c.matricula,
    car.titulo as cargo,
    s.nome_abreviado as sindicato,
    e.valor_vr_diario
FROM colaboradores c
JOIN cargos car ON c.cargo_id = car.id
JOIN sindicatos s ON c.sindicato_id = s.id
JOIN estados e ON s.estado_id = e.id
WHERE c.id NOT IN (SELECT colaborador_id FROM exclusoes)
AND c.situacao NOT IN ('Auxílio Doença', 'Licença Maternidade', 'Atestado')
AND car.categoria = 'FUNCIONARIO'
ORDER BY c.matricula;
```

### **Cálculo de VR com Férias**
```sql
SELECT 
    c.matricula,
    du.dias_uteis as dias_uteis_sindicato,
    COALESCE(f.dias_ferias, 0) as dias_ferias,
    (du.dias_uteis - COALESCE(f.dias_ferias, 0)) as dias_vr_calculados,
    (du.dias_uteis - COALESCE(f.dias_ferias, 0)) * e.valor_vr_diario as valor_total
FROM colaboradores c
JOIN sindicatos s ON c.sindicato_id = s.id
JOIN estados e ON s.estado_id = e.id
JOIN dias_uteis du ON s.id = du.sindicato_id
LEFT JOIN ferias f ON c.id = f.colaborador_id
WHERE c.id NOT IN (SELECT colaborador_id FROM exclusoes)
AND car.categoria = 'FUNCIONARIO';
```

## 🛠️ Manutenção

### **Verificar Integridade**
```bash
# Verificar se o banco existe e está íntegro
python3 database_connect.py
```

### **Backup Regular**
```bash
# Criar backup diário (recomendado)
python3 database_backup.py --backup

# Verificar backups
python3 database_backup.py --list
```

### **Limpeza de Backups**
```bash
# Remover backups com mais de 30 dias
python3 database_backup.py --cleanup 30
```

## 📈 Estatísticas do Banco

### **Dados Populados**
- **Colaboradores**: 1.815 ativos
- **Sindicatos**: 4 (PR, RS, SP, RJ)
- **Estados**: 4 com valores de VR
- **Cargos**: 188 diferentes categorizados
- **Férias**: 76 colaboradores
- **Afastamentos**: 20 colaboradores
- **Desligamentos**: 3 colaboradores
- **Admissões**: 73 novos colaboradores
- **Exclusões**: 64 (27 estagiários + 33 aprendizes + 4 exterior)

### **Valores de VR por Estado**
- **Paraná**: R$ 35,00
- **Rio de Janeiro**: R$ 35,00
- **Rio Grande do Sul**: R$ 35,00
- **São Paulo**: R$ 37,50

### **Dias Úteis por Sindicato**
- **SITEPD PR**: 22 dias úteis
- **SINDPPD RS**: 21 dias úteis
- **SINDPD SP**: 22 dias úteis
- **SINDPD RJ**: 21 dias úteis

## 🔧 Solução de Problemas

### **Erro: Banco não encontrado**
```
❌ Banco de dados não encontrado: vr_database.db
💡 Execute primeiro: python3 create_database.py
```

**Solução:** Execute `python3 create_database.py`

### **Erro: Planilhas não encontradas**
```
❌ [Errno 2] No such file or directory: 'data/ATIVOS.xlsx'
```

**Solução:** Verifique se a pasta `data/` existe com as planilhas Excel

### **Erro: Permissão negada**
```
❌ Permission denied: vr_database.db
```

**Solução:** Verifique permissões de escrita no diretório

### **Banco corrompido**
```bash
# Restaurar último backup
python3 database_backup.py --list
python3 database_backup.py --restore backups/ultimo_backup.zip
```

## 📋 Checklist de Implementação

- [ ] **Criar banco de dados**: `python3 create_database.py`
- [ ] **Verificar dados**: `python3 database_connect.py`
- [ ] **Criar backup inicial**: `python3 database_backup.py --backup`
- [ ] **Testar consultas**: Verificar resultados das consultas
- [ ] **Configurar backup automático**: Agendar backup regular
- [ ] **Documentar uso**: Compartilhar instruções com equipe

## 🚀 Próximos Passos

1. **Implementar algoritmo de cálculo** usando as tabelas criadas
2. **Criar interface de usuário** para visualização dos dados
3. **Implementar validações** de negócio no banco
4. **Criar relatórios** baseados nas views
5. **Implementar auditoria** de mudanças
6. **Otimizar performance** para grandes volumes

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique este README
2. Execute os scripts de diagnóstico
3. Consulte a documentação técnica (`README_database.md`)
4. Verifique os logs de erro

---

**Nota**: Este banco de dados foi projetado especificamente para o sistema de VR/VA, considerando todas as regras de negócio documentadas e os dados das planilhas Excel fornecidas.
