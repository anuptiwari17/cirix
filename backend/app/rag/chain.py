import time
from typing import List

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

from app.config import GEMINI_API_KEY, LLM_MODEL_NAME
from app.rag.retriever import retrieve_context
from app.rag.prompt import format_source_label 

#Session history: in-memory, TTL-pruned.

SESSION_TTL_SECONDS = 3600   #sessions unused for 1 hour get cleaned up
MAX_HISTORY_MESSAGES = 10    #last 5 exchanges (user + assistant)


class TTLChatHistory(BaseChatMessageHistory, BaseModel):
    """In-memory chat history for one session, auto-trimmed and TTL-pruned."""
    messages: List[BaseMessage] = Field(default_factory=list)
    last_used: float = Field(default_factory=time.time)

    def add_messages(self, messages: List[BaseMessage]) -> None:
        self.messages.extend(messages)
        self.messages = self.messages[-MAX_HISTORY_MESSAGES:]
        self.last_used = time.time()

    def clear(self) -> None:
        self.messages = []


_store: dict[str, TTLChatHistory] = {}


def _prune_expired_sessions():
    now = time.time()
    expired = [sid for sid, h in _store.items() if now - h.last_used > SESSION_TTL_SECONDS]
    for sid in expired:
        del _store[sid]


def _get_session_history(session_id: str) -> TTLChatHistory:
    _prune_expired_sessions()
    if session_id not in _store:
        _store[session_id] = TTLChatHistory()
    return _store[session_id]



#The LLM

llm = ChatGoogleGenerativeAI(model=LLM_MODEL_NAME, api_key=GEMINI_API_KEY)


#prompt. {context} is injected fresh on every call (see run_chat below);
#{history} is managed automatically by RunnableWithMessageHistory.

SYSTEM_PROMPT = """You are a helpful assistant that answers questions using ONLY the provided sources.

Rules:
- Answer using only the information in the sources below.
- Cite sources inline using their number, like [1] or [2], right after the claim they support.
- If the sources don't contain the answer, say so clearly instead of guessing.
- Be concise and direct.

Sources:
{context}"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{question}"),
])


#actual LCEL chain: prompt -> llm -> plain string output.
#Wrapped with history management so each session_id gets its own memory.

_base_chain = prompt | llm | StrOutputParser()

_chain_with_history = RunnableWithMessageHistory(
    _base_chain,
    _get_session_history,
    input_messages_key="question",
    history_messages_key="history",
)


def run_chat(session_id: str, question: str) -> dict:
    """
    Retrieves context, runs the LCEL chain (with per-session memory),
    and returns {answer, citations} -- same shape chat.py expects.
    """
    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    contexts = retrieve_context(question)

    if not contexts:
        context_text = (
            "No relevant sources found. Tell the user you have no sources "
            "to answer their question from."
        )
        citations = []
    else:
        blocks = []
        citations = []
        for i, ctx in enumerate(contexts, start=1):
            label = format_source_label(ctx["metadata"])
            blocks.append(f"[{i}] Source: {label}\n{ctx['text']}")
            citations.append({
                "label": label,
                "text": ctx["text"][:200],
                "metadata": ctx["metadata"],
            })
        context_text = "\n\n".join(blocks)

    try:
        answer = _chain_with_history.invoke(
            {"question": question, "context": context_text},
            config={"configurable": {"session_id": session_id}},
        )
    except Exception as e:
        #Covers transient failures: rate limits, network errors, quota
        #exceeded, etc. - surfaced as a clean error chat.py can turn
        # into a proper HTTP status instead of a raw 500 traceback.
        raise RuntimeError(f"LLM generation failed: {str(e)}") from e

    return {"answer": answer, "citations": citations}