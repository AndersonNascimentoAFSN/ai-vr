
# Automação de Benefícios VR/VA com Agentes Inteligentes

Este projeto automatiza o cálculo, validação e exportação dos benefícios de Vale Refeição (VR) e Vale Alimentação (VA) para colaboradores, integrando dados de banco SQLite, regras de convenção coletiva e agentes inteligentes (LangChain).

## O que o projeto faz?

1. **Cria e Popula o Banco de Dados**
    - Inicializa o banco SQLite com schema completo e dados das planilhas (colaboradores, sindicatos, cargos, férias, afastamentos, etc).
    - Scripts automatizados garantem que o banco esteja sempre atualizado e íntegro.

2. **Processa os Benefícios VR/VA**
    - Orquestrador executa todas as etapas: consulta, cálculo, aplicação de regras e exportação.
    - Recebe regras da convenção coletiva em JSON, permitindo ajustes dinâmicos por categoria, sindicato, limites, descontos, etc.

3. **Agentes Inteligentes**
    - **DatabaseAgent**: Realiza consultas SQL e integra com LLM (LangChain/OpenAI) para análises avançadas.
    - **ExportAgent**: Gera a base de cálculo dos benefícios consolidando dados do banco.
    - **ConvencaoAgent**: Aplica regras da convenção coletiva sobre os dados, ajustando valores, descontos e exceções.

4. **Exporta Relatórios**
    - Gera planilhas Excel prontas para uso em RH, financeiro ou auditoria.
    - Exportação automatizada e validada.

## Fluxo de Execução

1. **Verificação e Criação do Banco**
    - O sistema verifica se o banco existe. Se não, cria e popula automaticamente.

2. **Processamento dos Benefícios**
    - O orquestrador executa a função principal, processando os dados conforme regras da convenção.

3. **Aplicação das Regras**
    - Agentes aplicam regras específicas de negócio, incluindo exceções e limites definidos pelo usuário.

4. **Exportação**
    - Os dados finais são exportados para uma planilha Excel.

## Estrutura do Projeto

- `ai_vr/core/processar.py`: Orquestrador principal do fluxo de cálculo e exportação.
- `ai_vr/agents/db_agent.py`: Agente para consultas SQL e integração LLM.
- `ai_vr/agents/convencao_agent.py`: Aplica regras da convenção coletiva.
- `ai_vr/agents/export_agent.py`: Consolida e exporta dados.
- `ai_vr/scripts/generate_vr_planilha.py`: Gera base de cálculo e exportação.
- `ai_vr/scripts/database_populate.py`: Popula o banco a partir das planilhas.
- `ai_vr/scripts/database_backup.py`: Backup/restauração do banco.
- `ai_vr/db/database_schema.sql`: Schema completo do banco.
- `ai_vr/db/vr_database.db`: Banco de dados SQLite.
- `data/VR_MENSAL_GERADO.xlsx`: Planilha gerada.

## Instalação

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Uso

Execute o orquestrador diretamente:

```bash
python3 -m ai_vr.core.processar
```

Ou utilize a função programaticamente:

```python
from ai_vr.core.processar import processar_beneficios

convencao = {
     "valor_vr_diario_padrao": 37.5,
     "percentual_desconto_colaborador": 0.2,
     "percentual_custo_empresa": 0.8,
     "limites": {"max_desconto": 400.0},
     "excecoes": {
          "por_categoria": {"ESTAGIARIO": {"excluir": True}},
          "por_sindicato": {"SINDPD SP": {"valor_vr_diario": 40.0}}
     }
}

saida = processar_beneficios(
     db_path="ai_vr/db/vr_database.db",
     convencao_json=json.dumps(convencao),
     output_planilha="data/VR_MENSAL_GERADO.xlsx",
)
print("Gerado em:", saida)
```

## Observações

- A coluna `data_admissao` em `colaboradores` é sincronizada a partir de `admissoes` durante a população do banco.
- A exportação usa a função `salvar_planilha` do script existente; não é criada a aba "Validações".
- O projeto pode ser executado em modo offline (sem LLM) usando apenas o ExportAgent.

## Integração com LLM (LangChain/OpenAI)

- Configure a variável de ambiente `OPENAI_API_KEY` (ou crie um arquivo `.env` com essa variável).
- O DatabaseAgent utiliza essa chave para inicializar o cliente LLM.
- A execução do orquestrador pode consumir tokens/custos na conta associada à chave.

## Segurança e Customização

- O projeto permite ajustes dinâmicos nas regras de convenção coletiva via JSON.
- Testes locais podem ser feitos sem LLM.
- Para evitar inicialização do DatabaseAgent sem chave, pode-se adicionar modo "offline" ou flag CLI.

---
Projeto desenvolvido para automação, validação e exportação de benefícios VR/VA com máxima flexibilidade e integração inteligente.

