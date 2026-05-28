from langchain.memory import ConversationSummaryMemory
from langchain_community.chat_message_histories import InMemoryChatMessageHistory
from .client import get_llm
session_memories = {}
def get_memory(session_id: str):
    if session_id not in session_memories:
        history = InMemoryChatMessageHistory()
        memory = ConversationSummaryMemory(
            llm=get_llm(temperature=0),
            chat_memory=history,
            return_messages=True,
            memory_key="history",
            input_key="input"
        )
        session_memories[session_id] = memory
    return session_memories[session_id]
