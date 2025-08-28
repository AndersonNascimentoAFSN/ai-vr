# Automação de Benefícios VR/VA com LangChain

Este projeto automatiza o cálculo de benefícios VR/VA usando:
- Banco SQLite existente
- Scripts prontos de carga e exportação
- Agentes orquestrados com LangChain

## Estrutura
- `generate_vr_planilha.py`: script existente usado para ler o banco e gerar base de cálculo e exportação (sem aba de validações)
- `automation/agents/db_agent.py`: agente para consultas SQL via LangChain
- `automation/agents/convencao_agent.py`: aplica regras da convenção coletiva sobre o DataFrame
- `automation/agents/export_agent.py`: consolida e exporta usando o script existente
- `automation/processar.py`: função `processar_beneficios` que orquestra tudo

## Instalação
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Configure as credenciais do provedor LLM (OpenAI compatível) via variáveis de ambiente, se necessário, para o agente SQL do LangChain.

## Uso
```python
from automation.processar import processar_beneficios

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
    db_path="/home/andersonnascimento/develop/github/projects/ai_vr/vr_database.db",
    convencao_json=json.dumps(convencao),
    output_planilha="/home/andersonnascimento/develop/github/projects/ai_vr/data/VR_MENSAL_GERADO.xlsx",
)
print("Gerado em:", saida)
```

Ou rode o módulo diretamente (usa um exemplo de convenção):
```bash
python3 -m automation.processar
```

## Observações
- A coluna `data_admissao` em `colaboradores` é sincronizada a partir de `admissoes` durante a população do banco.
- A exportação usa a função `salvar_planilha` do script existente; não é criada a aba "Validações".

## Compatibilidade e mudanças recentes
Durante manutenção foi ajustado o import do cliente ChatOpenAI para a implementação recomentada.

- O arquivo `automation/agents/db_agent.py` agora importa `ChatOpenAI` de `langchain_openai` (em vez de `langchain` ou `langchain_community`).
- Para garantir compatibilidade, instale as dependências adicionais no ambiente virtual:

```bash
source .venv/bin/activate
pip install openai langchain-openai
```

Observação: ao atualizar `langchain`/`langchain-core` e pacotes relacionados, podem ocorrer avisos de compatibilidade entre versões (pydantic/langsmith/langchain-core). Se você preferir evitar atualizações grandes, pode reverter o import para `langchain_community.chat_models.ChatOpenAI` e manter as versões antigas:

```bash
# Reverter código (exemplo):
# from langchain_openai import ChatOpenAI
# ->
# from langchain_community.chat_models import ChatOpenAI

# Se trocar o import, mantenha as versões originais listadas em requirements.txt
```

Uso da chave do provedor LLM
- Configure a variável de ambiente `OPENAI_API_KEY` (ou crie um arquivo `.env` com essa variável). O orquestrador e `DatabaseAgent` usam essa chave para inicializar o cliente.

Exemplo mínimo (shell zsh):

```bash
# carregar .env (opcional se já setada)
set -a && source .env && set +a

# rodar orquestrador (gera planilha e usa o LLM)
python -m automation.processar
```

Segurança e custo
- A execução do orquestrador chama o LLM e pode consumir tokens/custos na conta associada à `OPENAI_API_KEY`. Testes locais sem LLM podem ser feitos usando apenas o `ExportAgent` (não exige chave).

Notas para desenvolvedores
- Se preferir que o projeto não inicialize o `DatabaseAgent` quando a chave não estiver presente, podemos adicionar um modo "offline" ou um flag CLI em `automation/processar.py`.

