import aiohttp
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from openai import AzureOpenAI
import re
import os
# from azure.identity import DefaultAzureCredential, get_bearer_token_provider

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

def generate_embeddings(text, model):
    client = AzureOpenAI(
        api_key = os.getenv('AZURE_OPENAI_EMBED_API_KEY'),  
        api_version = os.getenv('AZURE_OPENAI_EMBED_API_VERSION'),
        azure_endpoint = os.getenv('AZURE_OPENAI_EMBED_ENDPOINT')
    ) 
    return client.embeddings.create(input = [text], model=model).data[0].embedding

def get_similarity_with_embeddings(user_query,target_text):
    e_user_query = generate_embeddings(
        user_query,
        model=os.getenv('EMBED_MODEL_DEPLOYMENT_NAME')
    )

    e_target_text = generate_embeddings(
        target_text,
        model=os.getenv('EMBED_MODEL_DEPLOYMENT_NAME')
    )
    
    similarity_score = cosine_similarity_np(e_target_text, e_user_query)

    return similarity_score

def get_similarity_with_cosine(user_query,target_text):
    vectorizer = TfidfVectorizer().fit_transform([user_query, target_text])
    vectors = vectorizer.toarray()

    cossim = cosine_similarity(vectors)

    return cossim[0,1]

def get_similarity_with_tfidf(user_query,target_text):
    corpus = [user_query, 
        target_text]                                                                                                                                                                                                              
    vect = TfidfVectorizer(min_df=1, stop_words="english")                                                                                                                                                                                                   
    tfidf = vect.fit_transform(corpus)                                                                                                                                                                                                                       
    pairwise_similarity = tfidf * tfidf.T 
    return pairwise_similarity[1,0]

# get free photo links
# https://unsplash.com/developers

# async def fetch(session, url):
#     async with session.get(url) as response:
#         return await response.text()

# async def main():
#     async with aiohttp.ClientSession() as session:
#         html = await fetch(session, 'http://python.org')
#         print(html)

# # Python 3.7+
# if __name__ == '__main__':
#     asyncio.run(main())

async def asyncpostreq(url,headers=None,payloadstr=None,verb = "get"):
    data = ''
    if verb == "post":
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=payloadstr) as response:
                data = await response.read()
                # print(data.decode('utf8'))
    elif verb == "get":
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.read()
    
    return data.decode('utf8')

