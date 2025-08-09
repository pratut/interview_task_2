from pinecone import Pinecone
import os
from dotenv import load_dotenv
load_dotenv()
# Initialize Pinecone
pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
pinecone_index = pc.Index("booking")  # Must already exist in Pinecone