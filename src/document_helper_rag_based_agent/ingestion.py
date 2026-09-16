import asyncio
import os
import ssl
from typing import Dict,Any,List

import certifi
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_tavily import TavilyCrawl

from document_helper_rag_based_agent.logger import (Colors,log_error,log_header,log_info,log_success,log_warning)

load_dotenv()


ssl_context=ssl.create_default_context(cafile=certifi.where())
os.environ["SSL_CERT_FILE"]=certifi.where()
os.environ["REQUEST_CA_BUNDLE"]=certifi.where()

embeddings= OpenAIEmbeddings(
    model="nvidia/nemotron-3-embed-1b:free",
    openai_api_key=os.environ.get("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    check_embedding_ctx_length=False,
    chunk_size=50,
    retry_min_seconds=10
)

vectorstore=PineconeVectorStore(index_name=os.environ["INDEX_NAME"],embedding=embeddings)
tavily_crawl=TavilyCrawl()

async def index_document_async(documents:List[Document],batch_size=50):
        log_header("Storing chunks into vector database")
        log_info(f"Preparing to add {len(documents)} documents to vector db",Colors.DARKCYAN)

        batches=[documents[i:i+batch_size] for i in range(0,len(documents),batch_size)]

        #concurrently processing all batches
        async def add_batch(batch: List[Document],batch_num:int):
            try:
                await vectorstore.aadd_documents(batch)
                log_success(f"successfully add batch {batch_num}/{len(batches)} ({len(batch)}) documents")
            except Exception as e:
                log_error(f"vector store indexing failed to index batch- {batch_num} - {e}")
                return False
            return True

        tasks= [add_batch(batch,i+1) for i,batch in enumerate(batches)]
        results=await asyncio.gather(*tasks, return_exceptions=True)

        successful=sum(1 for result in results if result is True)

        if successful==len(batches):
            log_success(f"Sucessfully Indexed {successful}/{len(batches)}")
        else:
            log_warning(f"only {successful}/{len(batches)} processed")

async def main():
    log_header("Ingestion pipeline...")

    log_info("tavily crwal started", 
             Colors.PURPLE)

    crawl_result=tavily_crawl.invoke({
       "url": "https://r3f.docs.pmnd.rs/getting-started/introduction",
        "max-depth": 3,
        "extract-depth":"advanced",
        })
    print(type(crawl_result))
    
    
    #all_docs=[Document(page_content=result['raw_content'],metadata={"source":result['url']}) for result in crawl_result['results']]
    all_docs = []

    for result in crawl_result["results"]:
        if not result.get("raw_content"):
            log_warning(
                f"Skipping page with no content: {result.get('url')}")
            continue

        all_docs.append(
            Document(
                page_content=result["raw_content"],
                metadata={"source": result["url"]}
            )
        )
    log_success(f"Tavily crawl successfully searched {len(all_docs)} URLs.")

    log_info("Chunking the document",Colors.YELLOW)

    text_splitter=RecursiveCharacterTextSplitter(chunk_size=4000,chunk_overlap=200)
    splitted_docs=text_splitter.split_documents(all_docs)

    log_success(f"splitted {len(splitted_docs)} chunks from {len(all_docs)} documents.")


    await index_document_async(splitted_docs,batch_size=500)

    log_header("Pipeline Complete!")




    
if __name__=="__main__":
    asyncio.run(main())