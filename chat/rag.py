# Retrieval Augmented Generation 코드를 여기에 작성합니다.

from typing import List
from langchain import OpenAI, SQLDatabase
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_experimental.sql import SQLDatabaseChain
from langchain.chains.router import MultiPromptChain
from langchain.llms import OpenAI
from langchain.chains import ConversationChain
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chains.router.llm_router import LLMRouterChain, RouterOutputParser
from langchain.chains.router.multi_prompt_prompt import MULTI_PROMPT_ROUTER_TEMPLATE
from pydantic import BaseModel

import my_settings


class RAG(BaseModel) :
    query: str

    SQL_prompt_template:str = """
        Given an input question, first create a syntactically correct postgresql query to run, then look at the results of the query and return the answer.
        Use the following format:

        Question: Question here
        SQLQuery: SQL Query to run
        SQLResult: Result of the SQLQuery
        Answer: Final answer here

        {query}"""

    dummy_prompt_template:str = """
        Tell me a joke with following words.
         
        {query}"""

    prompt_infos:List[dict] = [
        {
            "name" : "db_chain",
            "description" : "Good for answering questions about instance billing or instance usages",
            "prompt_template" : SQL_prompt_template
        },
        {
            "name": "dummy_chain",
            "description": "Good for answering questions about making a joke",
            "prompt_template": dummy_prompt_template
        }
    ]

    def get_sentence(self):

        SQL_db = SQLDatabase.from_uri(my_settings.RAG_DB_INFO)
        llm = OpenAI(streaming=True, callbacks=[StreamingStdOutCallbackHandler()], temperature=0, verbose=True)
        db_chain = SQLDatabaseChain.from_llm(llm, SQL_db, verbose=True)

        return db_chain(self.query)['result']


    def get_sentence_from_MultiPromptChain(self):
        """
        MultiPromptChain을 통해서 similarity 기반의 의도 분류기 역할을 수행하고자 한다.

        이슈 사항으로는, MultiPromptChain에서 SQLDatabaseChain은 지원하지 않는 듯..
        단순 LLMChain만 지원하는 것으로 보여지니 확인이 필요함.
        """

        llm = OpenAI(streaming=True, callbacks=[StreamingStdOutCallbackHandler()], temperature=0, verbose=True)

        destination_chains = {}

        SQL_db = SQLDatabase.from_uri(my_settings.RAG_DB_INFO)
        db_chain_prompt = PromptTemplate(template=self.SQL_prompt_template, input_variables=["query"])
        db_chain = SQLDatabaseChain.from_llm(llm, SQL_db, prompt=db_chain_prompt, verbose=True)
        destination_chains['db_chain'] = db_chain

        dummy_chain_prompt = PromptTemplate(template=self.dummy_prompt_template, input_variables=["query"])
        dummy_chain = LLMChain(llm=llm, prompt=dummy_chain_prompt)
        destination_chains['dummy_chain'] = dummy_chain

        default_chain = ConversationChain(llm=llm, output_key="text")


        destinations = [f"{p['name']}: {p['description']}" for p in self.prompt_infos]
        destinations_str = "\n".join(destinations)
        router_template = MULTI_PROMPT_ROUTER_TEMPLATE.format(destinations=destinations_str)
        router_prompt = PromptTemplate(
            template=router_template,
            input_variables=["input"],
            output_parser=RouterOutputParser(),
        )
        router_chain = LLMRouterChain.from_llm(llm, router_prompt)

        # 에러 발생 : MultiPromptChain의 destination_chain이 SQLDatabaseChain을 지원하지 않는 듯
        chain = MultiPromptChain(
            router_chain=router_chain,
            destination_chains=destination_chains,
            default_chain=default_chain,
            verbose=True,
        )
        print(chain)
        return chain(self.query)['result']