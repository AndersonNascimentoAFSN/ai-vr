# Documentação: Automação da Compra de VR/VA

## 📋 Visão Geral do Problema

### O que é VR/VA?
- **VR (Vale Refeição)**: Benefício fornecido pela empresa para auxiliar na alimentação dos colaboradores
- **VA (Vale Alimentação)**: Similar ao VR, mas com regras específicas
- **Objetivo**: Garantir que cada colaborador receba o valor correto de VR, considerando ausências, férias, datas de admissão/desligamento e calendário de feriados

### Por que Automatizar?
Atualmente, o cálculo é feito manualmente através de planilhas, o que envolve:
- Conferência manual de datas de início e fim de contrato
- Exclusão manual de colaboradores em férias
- Cálculo manual de dias proporcionais
- Geração manual do layout para o fornecedor
- Verificação manual das regras de cada sindicato

## 📊 Estrutura dos Dados

### Planilhas Disponíveis

#### 1. **ATIVOS.xlsx** (1.815 colaboradores)
**Propósito**: Base principal de todos os colaboradores ativos
**Colunas**:
- `MATRICULA`: Identificação única do colaborador
- `EMPRESA`: Código da empresa
- `TITULO DO CARGO`: Cargo do colaborador
- `DESC. SITUACAO`: Situação atual (Trabalhando, Férias, etc.)
- `Sindicato`: Sindicato ao qual o colaborador está vinculado

#### 2. **FÉRIAS.xlsx** (80 colaboradores)
**Propósito**: Colaboradores em férias no mês
**Colunas**:
- `MATRICULA`: Identificação do colaborador
- `DESC. SITUACAO`: Situação (Férias)
- `DIAS DE FÉRIAS`: Quantidade de dias de férias

#### 3. **DESLIGADOS.xlsx** (51 colaboradores)
**Propósito**: Colaboradores que foram desligados
**Colunas**:
- `MATRICULA`: Identificação do colaborador
- `DATA DEMISSÃO`: Data do desligamento
- `COMUNICADO DE DESLIGAMENTO`: Status do comunicado (OK ou não)

#### 4. **ADMISSÃO ABRIL.xlsx** (83 colaboradores)
**Propósito**: Novos colaboradores admitidos em abril
**Colunas**:
- `MATRICULA`: Identificação do colaborador
- `Admissão`: Data de admissão
- `Cargo`: Cargo do colaborador

#### 5. **AFASTAMENTOS.xlsx** (20 colaboradores)
**Propósito**: Colaboradores afastados por diversos motivos
**Colunas**:
- `MATRICULA`: Identificação do colaborador
- `DESC. SITUACAO`: Tipo de afastamento (Licença Maternidade, Auxílio Doença, etc.)
- `na compra?`: Se deve ser incluído na compra de VR

#### 6. **ESTÁGIO.xlsx** (27 colaboradores)
**Propósito**: Lista de estagiários
**Colunas**:
- `MATRICULA`: Identificação do colaborador
- `TITULO DO CARGO`: Cargo (ESTAGIARIO)
- `na compra?`: Se deve ser incluído na compra de VR

#### 7. **APRENDIZ.xlsx** (33 colaboradores)
**Propósito**: Lista de aprendizes
**Colunas**:
- `MATRICULA`: Identificação do colaborador
- `TITULO DO CARGO`: Cargo (APRENDIZ)

#### 8. **EXTERIOR.xlsx** (4 colaboradores)
**Propósito**: Colaboradores que atuam no exterior
**Colunas**:
- `Cadastro`: Identificação do colaborador
- `Valor`: Valor específico para colaboradores no exterior
- `Unnamed: 2`: Observações sobre o status

#### 9. **Base sindicato x valor.xlsx** (4 registros)
**Propósito**: Valores de VR por estado/sindicato
**Colunas**:
- `ESTADO`: Estado (Paraná, Rio de Janeiro, Rio Grande do Sul, São Paulo)
- `VALOR`: Valor diário do VR por estado

#### 10. **Base dias uteis.xlsx** (4 registros)
**Propósito**: Quantidade de dias úteis por sindicato (BASE DIAS UTEIS DE 15/04 a 15/05)
**Colunas**:
- `SINDICADO`: Nome do sindicato
- `DIAS UTEIS`: Quantidade de dias úteis (22 para PR, 21 para RS, 21 para SP, 21 para RJ)

#### 11. **VR MENSAL 05.2025.xlsx** (1.860 linhas)
**Propósito**: Planilha final com cálculos e validações
**Abas**:
- **VR MENSAL 05.2025**: Dados calculados
- **Validações**: Lista de verificações necessárias

## 🎯 Regras de Negócio Detalhadas

### 1. Regras de Exclusão (Quem NÃO recebe VR)

#### 1.1 Cargos Excluídos
- **Diretores**: Todos os cargos de direção
- **Estagiários**: Colaboradores com cargo "ESTAGIARIO"
- **Aprendizes**: Colaboradores com cargo "APRENDIZ"

#### 1.2 Situações de Afastamento
- **Licença Maternidade**: Colaboradores em licença maternidade
- **Auxílio Doença**: Colaboradores em auxílio doença
- **Outros Afastamentos**: Qualquer tipo de afastamento que não seja férias

#### 1.3 Colaboradores no Exterior
- Todos os colaboradores que atuam no exterior (baseado na planilha EXTERIOR.xlsx)

### 2. Regras de Cálculo de Dias

#### 2.1 Dias Úteis por Sindicato
- **SITEPD PR - SIND DOS TRAB EM EMPR PRIVADAS DE PROC DE DADOS DE CURITIBA E REGIAO METROPOLITANA**: 22 dias úteis
- **SINDPPD RS - SINDICATO DOS TRAB. EM PROC. DE DADOS RIO GRANDE DO SUL**: 21 dias úteis
- **SINDPD SP - SIND.TRAB.EM PROC DADOS E EMPR.EMPRESAS PROC DADOS ESTADO DE SP.**: 22 dias úteis
- **SINDPD RJ - SINDICATO PROFISSIONAIS DE PROC DADOS DO RIO DE JANEIRO**: 21 dias úteis

#### 2.2 Redução por Férias
- Se o colaborador está de férias, os dias de férias são **subtraídos** dos dias úteis
- **Exemplo**: Colaborador com 22 dias úteis e 10 dias de férias = 12 dias de VR

#### 2.3 Admissões no Mês
- Colaboradores admitidos no mês recebem VR **proporcional** aos dias trabalhados
- **Cálculo**: (Dias úteis do mês - Dias de férias) × (Dias trabalhados / Dias úteis do mês)

#### 2.4 Desligamentos no Mês
- **Se comunicado até dia 15**: Não recebe VR
- **Se comunicado após dia 15**: Recebe VR proporcional aos dias trabalhados
- **Cálculo**: (Dias úteis do mês - Dias de férias) × (Dias trabalhados / Dias úteis do mês)

### 3. Regras de Valor

#### 3.1 Valor Diário
- **Valores por estado**:
  - **Paraná**: R$ 35,00 por dia
  - **Rio de Janeiro**: R$ 35,00 por dia
  - **Rio Grande do Sul**: R$ 35,00 por dia
  - **São Paulo**: R$ 37,50 por dia
- **Base**: Planilha "Base sindicato x valor.xlsx"

#### 3.2 Cálculo do Valor Total
```
Valor Total = Dias de VR × Valor Diário do Estado
```
**Onde o Valor Diário varia por estado conforme a planilha "Base sindicato x valor.xlsx"**

#### 3.3 Distribuição de Custos
- **Empresa**: Paga 80% do valor total
- **Colaborador**: Paga 20% do valor total (descontado do salário)

**Exemplo (São Paulo)**:
- Dias de VR: 22
- Valor diário: R$ 37,50
- Valor total: R$ 825,00
- Custo empresa: R$ 660,00 (80%)
- Desconto colaborador: R$ 165,00 (20%)

**Exemplo (Paraná/Rio de Janeiro/Rio Grande do Sul)**:
- Dias de VR: 22
- Valor diário: R$ 35,00
- Valor total: R$ 770,00
- Custo empresa: R$ 616,00 (80%)
- Desconto colaborador: R$ 154,00 (20%)

## 🔄 Processo de Cálculo Passo a Passo

### Passo 1: Consolidação das Bases
1. **Base Principal**: Usar ATIVOS.xlsx como base
2. **Adicionar Admissões**: Incluir colaboradores de ADMISSÃO ABRIL.xlsx
3. **Adicionar Férias**: Incluir informações de FÉRIAS.xlsx
4. **Adicionar Desligamentos**: Incluir informações de DESLIGADOS.xlsx

### Passo 2: Aplicar Exclusões
1. **Excluir Estagiários**: Remover colaboradores da planilha ESTÁGIO.xlsx
2. **Excluir Aprendizes**: Remover colaboradores da planilha APRENDIZ.xlsx
3. **Excluir Afastados**: Remover colaboradores da planilha AFASTAMENTOS.xlsx
4. **Excluir Exterior**: Remover colaboradores da planilha EXTERIOR.xlsx

### Passo 3: Calcular Dias de VR
Para cada colaborador:

1. **Obter dias úteis do sindicato**:
   - Consultar Base dias uteis.xlsx
   - PR: 22 dias, RS: 21 dias, SP: 22 dias, RJ: 21 dias

2. **Subtrair dias de férias** (se aplicável):
   - Consultar FÉRIAS.xlsx
   - Dias VR = Dias úteis - Dias de férias

3. **Ajustar para admissões** (se aplicável):
   - Consultar ADMISSÃO ABRIL.xlsx
   - Calcular proporção de dias trabalhados

4. **Ajustar para desligamentos** (se aplicável):
   - Consultar DESLIGADOS.xlsx
   - Verificar data do comunicado
   - Calcular proporção se após dia 15

### Passo 4: Calcular Valores
1. **Obter valor diário do estado**: Consultar Base sindicato x valor.xlsx
2. **Valor total**: Dias VR × Valor Diário do Estado
3. **Custo empresa**: Valor total × 80%
4. **Desconto colaborador**: Valor total × 20%

### Passo 5: Gerar Planilha Final
Criar planilha com as colunas:
- Matrícula
- Admissão
- Sindicato do Colaborador
- Competência
- Dias
- VALOR DIÁRIO VR
- TOTAL
- Custo empresa
- Desconto profissional
- OBS GERAL

## ✅ Validações Necessárias

### 1. Validações de Dados
- [ ] Verificar se todas as matrículas existem na base principal
- [ ] Validar datas de admissão e desligamento
- [ ] Verificar se não há matrículas duplicadas
- [ ] Validar se os valores estão dentro do esperado

### 2. Validações de Regras
- [ ] Confirmar que estagiários e aprendizes foram excluídos
- [ ] Verificar se afastados foram removidos
- [ ] Validar cálculos de dias proporcionais
- [ ] Confirmar regras de desligamento (antes/depois do dia 15)

### 3. Validações de Resultado
- [ ] Total de colaboradores processados
- [ ] Soma dos valores totais
- [ ] Distribuição de custos (80%/20%)
- [ ] Verificar se não há valores negativos

## 📝 Exemplos Práticos

### Exemplo 1: Colaborador Normal (São Paulo)
- **Matrícula**: 34914
- **Sindicato**: SINDPD SP
- **Dias úteis**: 22
- **Férias**: 0 dias
- **Cálculo**: 22 × R$ 37,50 = R$ 825,00
- **Empresa**: R$ 660,00
- **Colaborador**: R$ 165,00

### Exemplo 2: Colaborador com Férias
- **Matrícula**: 32104
- **Sindicato**: SINDPPD RS
- **Dias úteis**: 21
- **Férias**: 10 dias
- **Cálculo**: (21 - 10) × R$ 35,00 = 11 × R$ 35,00 = R$ 385,00
- **Empresa**: R$ 308,00
- **Colaborador**: R$ 77,00

### Exemplo 3: Colaborador Admitido no Mês (São Paulo)
- **Matrícula**: 35741
- **Data admissão**: 07/04/2025
- **Sindicato**: SINDPD SP
- **Dias úteis**: 22
- **Dias trabalhados**: 15 (de 07/04 a 30/04)
- **Cálculo**: 22 × (15/22) × R$ 37,50 = 15 × R$ 37,50 = R$ 562,50
- **Empresa**: R$ 450,00
- **Colaborador**: R$ 112,50

### Exemplo 4: Colaborador Desligado
- **Matrícula**: 34706
- **Data desligamento**: 01/05/2025
- **Comunicado**: OK (antes do dia 15)
- **Resultado**: Não recebe VR (0 dias)

## 🚀 Benefícios da Automação

### Antes (Manual)
- ⏰ 2-3 dias de trabalho manual
- ❌ Alto risco de erros
- 🔄 Difícil manutenção
- 📊 Dificuldade para auditoria

### Depois (Automatizado)
- ⚡ Processo em minutos
- ✅ Redução significativa de erros
- 🔧 Fácil manutenção e ajustes
- 📈 Rastreabilidade completa
- 💰 Economia de tempo e recursos

## 📋 Checklist de Implementação

- [ ] Desenvolver sistema de consolidação de bases
- [ ] Implementar regras de exclusão
- [ ] Criar algoritmo de cálculo de dias
- [ ] Desenvolver sistema de validações
- [ ] Criar interface para geração da planilha final
- [ ] Implementar sistema de auditoria
- [ ] Criar documentação técnica
- [ ] Realizar testes com dados reais
- [ ] Treinar equipe de uso
- [ ] Implementar em produção

---

**Nota**: Esta documentação deve ser atualizada conforme mudanças nas regras de negócio ou estrutura dos dados.
