import re
from openai import AzureOpenAI
import pandas as pd
import os
import tiktoken
import numpy as np

AZURE_OPENAI_API_KEY = "1f90ee7386024a59a413ad7101326cd1"
AZURE_OPENAI_ENDPOINT = "https://alvaz-openai.openai.azure.com/"

client = AzureOpenAI(
  api_key = AZURE_OPENAI_API_KEY,  
  api_version = "2024-02-01",
  azure_endpoint = AZURE_OPENAI_ENDPOINT
)

# s is input text
def normalize_text(s, sep_token = " \n "):
    s = re.sub(r'\s+',  ' ', s).strip()
    s = re.sub(r". ,","",s)
    # remove all instances of multiple spaces
    s = s.replace("..",".")
    s = s.replace(". .",".")
    s = s.replace("\n", "")
    s = s.strip()
    
    return s

def cosine_similarity_np(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def generate_embeddings(text, model="text-embedding-ada-deployment"): # model = "deployment_name"
    return client.embeddings.create(input = [text], model=model).data[0].embedding

def calculate_similarity(user_query,target_text):
    e_user_query = generate_embeddings(
        user_query,
        model="text-embedding-ada-deployment" # model should be set to the deployment name you chose when you deployed the text-embedding-ada-002 (Version 2) model
    )

    e_target_text = generate_embeddings(
        target_text,
        model="text-embedding-ada-deployment" # model should be set to the deployment name you chose when you deployed the text-embedding-ada-002 (Version 2) model
    )
    
    similarity_score = cosine_similarity_np(e_target_text, e_user_query)

    return similarity_score

