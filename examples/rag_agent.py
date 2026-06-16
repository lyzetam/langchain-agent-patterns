"""
RAG Agent Example
=================
A Retrieval-Augmented Generation agent for document Q&A.
"""

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
import bs4


# Global vector store (in production, use persistent storage)
vector_store = None


def setup_knowledge_base():
    """Load and index documents."""
    global vector_store
    
    # Load documents from web
    loader = WebBaseLoader(
        web_paths=("https://lilianweng.github.io/posts/2023-06-23-agent/",),
        bs_kwargs=dict(
            parse_only=bs4.SoupStrainer(
                class_=("post-content", "post-title", "post-header")
            )
        ),
    )
    docs = loader.load()
    
    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    splits = text_splitter.split_documents(docs)
    
    # Create vector store
    embeddings = OpenAIEmbeddings()
    vector_store = FAISS.from_documents(splits, embeddings)
    
    print(f"Indexed {len(splits)} document chunks")


@tool(response_format="content_and_artifact")
def retrieve_context(query: str):
    """Retrieve information from the knowledge base to answer questions.
    
    Args:
        query: The user's question or search query
    
    Returns:
        Relevant document chunks with source information
    """
    if vector_store is None:
        return "Error: Knowledge base not initialized", []
    
    # Retrieve relevant documents
    retrieved_docs = vector_store.similarity_search(query, k=3)
    
    # Format for display
    serialized = "\n\n---\n\n".join(
        f"Source: {doc.metadata.get('source', 'Unknown')}\nContent: {doc.page_content}"
        for doc in retrieved_docs
    )
    
    return serialized, retrieved_docs


def main():
    # Setup knowledge base
    print("Setting up knowledge base...")
    setup_knowledge_base()
    
    # Create RAG agent
    agent = create_agent(
        model="anthropic:claude-sonnet-4-6",  # embeddings below still use OpenAI
        tools=[retrieve_context],
        system_prompt="""You are a helpful research assistant with access to a document about AI Agents.
        
Use the retrieve_context tool to find relevant information before answering questions.
Base your answers on the retrieved content and cite sources when possible.
If the retrieved content doesn't contain the answer, say so clearly."""
    )
    
    print("\nRAG Agent Ready - Ask questions about AI Agents")
    print("Type 'quit' to exit")
    print("-" * 50)
    
    while True:
        user_input = input("\nQuestion: ").strip()
        if user_input.lower() in ["quit", "exit", "q"]:
            break
        
        # Stream the response
        print("\nAnswer: ", end="", flush=True)
        
        for stream_mode, data in agent.stream(
            {"messages": [{"role": "user", "content": user_input}]},
            stream_mode=["updates", "messages"]
        ):
            if stream_mode == "messages":
                token, metadata = data
                if hasattr(token, 'content') and token.content:
                    print(token.content, end="", flush=True)
            
            elif stream_mode == "updates":
                for node, update in data.items():
                    if node == "tools":
                        print("\n[Retrieving relevant documents...]\n", flush=True)
        
        print("\n")


if __name__ == "__main__":
    main()
