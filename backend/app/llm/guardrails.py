from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from .client import get_llm
GUARD_PROMPT = PromptTemplate.from_template(
    "Is the following question related to inventory management? Reply only 'RELEVANT' or 'NOT_RELEVANT'.\nQuestion: {question}"
)
llm = get_llm(temperature=0)
chain = GUARD_PROMPT | llm | StrOutputParser()
def is_relevant(question: str) -> bool:
    return chain.invoke({"question": question}).strip().upper() == "RELEVANT"
