# summarizer.py

from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain_community.llms import HuggingFaceEndpoint
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")

if not HUGGINGFACE_TOKEN:
    raise ValueError("HUGGINGFACE_TOKEN not set in .env")

# Set up Hugging Face inference endpoint
llm = HuggingFaceEndpoint(
    repo_id="HuggingFaceH4/zephyr-7b-beta",
    huggingfacehub_api_token=HUGGINGFACE_TOKEN,
    task="text-generation",
    temperature=0.5,
    max_new_tokens=512,
    do_sample=True,
    top_p=0.95
)

def summarize_file(file_path: str) -> str:
    # Load the document
    if file_path.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    elif file_path.endswith(".docx"):
        loader = Docx2txtLoader(file_path)
    else:
        raise ValueError("Unsupported file format: only PDF and DOCX supported.")

    documents = loader.load()

    # Split into manageable chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = splitter.split_documents(documents)

    # Use map-reduce summarization
    chain = load_summarize_chain(llm, chain_type="map_reduce")

    # Generate and return the summary
    return chain.run(docs)
