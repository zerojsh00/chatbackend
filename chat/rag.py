# Retrieval Augmented Generation 코드를 여기에 작성합니다.

from langchain import OpenAI, SQLDatabase
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_experimental.sql import SQLDatabaseChain


class RAG:
    def __init__(self, query, db_info):
        self.query = query
        self.db_info = db_info

    def get_SQLDatabaseChain_result(self):

        prompt_template = """
        Given an input question, first create a syntactically correct postgresql query to run, then look at the results of the query and return the answer.
        Use the following format:

        Question: Question here
        SQLQuery: SQL Query to run
        SQLResult: Result of the SQLQuery
        Answer: Final answer here

        {query}
        """

        prompt = prompt_template.format(query=self.query)

        db = SQLDatabase.from_uri(self.db_info)
        llm = OpenAI(streaming=True, callbacks=[StreamingStdOutCallbackHandler()], temperature=0, verbose=True)

        db_chain = SQLDatabaseChain.from_llm(llm, db, verbose=True)
        return db_chain(prompt)['result']