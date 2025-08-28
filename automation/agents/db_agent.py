from typing import Optional
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI


class DatabaseAgent:
    """Agente responsável por consultar o banco SQLite via LangChain."""

    def __init__(self, db_path: str, llm_model: str = "gpt-4o-mini", temperature: float = 0.0):
        self.db = SQLDatabase.from_uri(f"sqlite:///{db_path}")
        self.llm = ChatOpenAI(model=llm_model, temperature=temperature)
        self.toolkit = SQLDatabaseToolkit(db=self.db, llm=self.llm)
        self.agent_executor = create_sql_agent(llm=self.llm, toolkit=self.toolkit, verbose=False)

    def run(self, question: str) -> str:
        return self.agent_executor.run(question)

    def get_connection_uri(self) -> str:
        return self.db._engine.url.render_as_string(hide_password=True)
