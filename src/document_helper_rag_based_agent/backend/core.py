import os 
from typing import Any, Dict

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.messages import ToolMessage
from langchain.tools import tool
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_openrouter import ChatOpenRouter
load_dotenv()

embeddings= OpenAIEmbeddings(
    model="nvidia/nemotron-3-embed-1b:free",
    openai_api_key=os.environ.get("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    check_embedding_ctx_length=False,
    chunk_size=50,
    retry_min_seconds=10
)

vectorstore=PineconeVectorStore(index_name=os.environ["INDEX_NAME"], embedding=embeddings)

#model=init_chat_model("openai/gpt-oss-120b",model_provider="groq",)
'''model = init_chat_model(
     "openrouter/free",
    model_provider="openrouter",
    timeout=120,
)'''

model = init_chat_model(
    "gemini-3.1-flash-lite",
    model_provider="google_genai",
)

@tool(response_format="content_and_artifact")
def retrieve_context(query:str):
    """retrieve relevant documents to helo user aswer queries about React Three Fibre"""
    retrieved_docs = vectorstore.as_retriever().invoke(query, k=2)

    serialized="\n\n".join(
        (f"Source:{doc.metadata.get('source','Unknown')}\n\n Content:{doc.page_content}")
        for doc in retrieved_docs
    )
    return serialized,retrieved_docs

def run_llm(query:str)->Dict[str,Any]:
    system_prompt=( 
        "You are a helpful AI assistant that answers questions about React Three Fibre documentation. "
        "You have access to a tool that retrieves relevant documentation. "
        "Use the tool to find relevant information before answering questions. "
        "Always cite the sources you use in your answers. "
        "If you cannot find the answer in the retrieved documentation, say so."
        )
    agent=create_agent(model,tools=[retrieve_context],system_prompt=system_prompt)

    messages=[{"role":"user","content":query}]

    response=agent.invoke({"messages":messages})

    answer=response["messages"][-1].content

    context_docs=[]

    for message in response["messages"]:
        if (isinstance(message,ToolMessage) and hasattr(message,"artifact")):
            if isinstance(message.artifact, list):
                context_docs.extend(message.artifact)

    raw_answer = response["messages"][-1].content

    if isinstance(raw_answer, list):
        answer = "\n".join(
            item["text"]
            for item in raw_answer
            if isinstance(item, dict) and item.get("type") == "text"
        )
    else:
        answer = str(raw_answer)    
    return {
        "answer":answer,
        "context":context_docs
    }

if __name__ == '__main__':
    result = run_llm(query="What are different types Materials?")
    print(result)

  