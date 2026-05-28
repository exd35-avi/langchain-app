from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from ..tools.inventory_tools import get_current_stock, get_sales_trend, recommend_reorder
from ..tools.forecast_tools import ml_demand_forecast, predict_stockout_risk
from ..tools.web_search import web_search
from ..tools.order_tools import create_purchase_order
from .client import get_llm
from .memory import get_memory

tools = [
    get_current_stock,
    get_sales_trend,
    ml_demand_forecast,
    predict_stockout_risk,
    recommend_reorder,
    create_purchase_order,
    web_search,
]

SYSTEM_PROMPT = """You are an inventory management assistant. Use the provided tools to answer questions accurately.
- For future demand predictions, use ml_demand_forecast (which uses Random Forest ML).
- For stockout probability, use predict_stockout_risk.
- For reorder recommendations, use recommend_reorder.
- Always include a disclaimer that predictions may vary based on real-world factors.
- If a question is not inventory-related, politely decline.
- If no tool can answer, fall back to web_search.
- Be concise and helpful."""

def get_agent(session_id: str):
    llm = get_llm(temperature=0.3)
    memory = get_memory(session_id)
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=False,
        handle_parsing_errors=True,
        max_iterations=5,
    )
