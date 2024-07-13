import azure.functions as func
import json
import logging
import inspect
import requests
import csv
import random
# import openai
import os
from dotenv import load_dotenv
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
import aiohttp
import asyncio
import re
import numpy as np

load_dotenv()  # take environment variables from .env.

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)
VOCABULARY_FILE = 'data/VOCABULARY.csv'

client = AzureOpenAI(
  api_key = os.getenv('AZURE_OPENAI_API_KEY_2'),  
  api_version = os.getenv('AZURE_OPENAI_API_VERSION_2'),
  azure_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT_2') 
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

def get_similarity_score(user_query,target_text):
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

##### Azure functions definitions ###################################################################

@app.route(route="expression_list")
def expression_list(req: func.HttpRequest) -> func.HttpResponse:
    if os.getenv("ENVIRONMENT") == "development":
        print(f'HTTP trigger function {inspect.currentframe().f_code.co_name} processed a request.')
    else:
        logging.info(f'HTTP trigger function {inspect.currentframe().f_code.co_name} processed a request.')

    result = []
    with open(VOCABULARY_FILE, 'r') as file:
        # Create a CSV reader
        reader = csv.reader(file)
    
        # Loop over each row in the file
        skipfirst = True
        for row in reader:
            if skipfirst:
                skipfirst = False
                continue
            item = {}
            item['word'] = row[1]
            item['stem'] = row[2]
            result.append(item)

    # Serialize data to JSON
    json_data = json.dumps(result)
    if os.getenv("ENVIRONMENT") == "development":
        print(f'Function returns: {json_data}')
    return func.HttpResponse(
        body=json_data,
        mimetype="application/json",
        status_code=200)

@app.route(route="random_expression")
def random_expression(req: func.HttpRequest) -> func.HttpResponse:
    if os.getenv("ENVIRONMENT") == "development":
        print(f'HTTP trigger function {inspect.currentframe().f_code.co_name} processed a request.')
    else:
        logging.info(f'HTTP trigger function {inspect.currentframe().f_code.co_name} processed a request.')

    result = []
    rowno = 0
    try:
        with open(VOCABULARY_FILE, 'r') as file:
            # Create a CSV reader
            reader = csv.reader(file)
        
            # Loop over each row in the file
            skipfirst = True
            for row in reader:
                if skipfirst:
                    skipfirst = False
                    continue
                item = {}
                item['word'] = row[0]
                item['stem'] = row[1]
                result.append(item)
                rowno += 1

        # Pick up random set from the array
        random_word = random.choice(result)
        status_code = 200
    except Exception as e:
        random_word = {"error" : f'At row_no {rowno}:{e}'}
        status_code = 500

    # Serialize data to JSON
    json_data = json.dumps(random_word)
    if os.getenv("ENVIRONMENT") == "development":
        print(f'Function returns: {json_data}')
    return func.HttpResponse(
        body=json_data,
        mimetype="application/json",
        status_code=status_code)

@app.route(route="expression_dictionary_definition", auth_level=func.AuthLevel.FUNCTION)
def expression_dictionary_definition(req: func.HttpRequest) -> func.HttpResponse:
    if os.getenv("ENVIRONMENT") == "development":
        print(f'HTTP trigger function {inspect.currentframe().f_code.co_name} processed a request.')
    else:
        logging.info(f'HTTP trigger function {inspect.currentframe().f_code.co_name} processed a request.')

    result = {}

    expression = req.params.get('expression')
    if not expression:
        try:
            req_body = req.get_json()
            expression = req_body.get('expression')
        except ValueError:
            req_error = {'error' : 'Request failed due to missing parameter [expression]'}
            # Serialize data to JSON
            return func.HttpResponse(
                body=json.dumps(req_error),
                mimetype="application/json",
                status_code=200)
        
    try:
        # Make a GET request to the API
        # response = requests.get(f'{os.getenv("FREE_DICTIONAY_API_BASE_URL")}{expression}',verify=False)
        response_text = asyncio.run(asyncpostreq(f'{os.getenv("FREE_DICTIONAY_API_BASE_URL")}{expression}'))
        response_json = json.loads(response_text)
    
        # Do something with 'data'
        definitions = response_json[0]['meanings'][0]['definitions']
        meanings = ''
        synonyms = ''
        for definition in definitions:
            meanings += f'{definition["definition"]}\n'
            synonyms += '\n'.join(definition["synonyms"])
        
        result['meanings'] = meanings
        result['synonyms'] = synonyms
                
        # Serialize data to JSON
        json_data = json.dumps(result)
        if os.getenv("ENVIRONMENT") == "development":
            print(f'Function {inspect.currentframe().f_code.co_name} returns: {json_data}')
        return func.HttpResponse(
            body=json_data,
            mimetype="application/json",
            status_code=200) 
    except Exception as e:
        result = {"error" : f'{e}'}
        # Serialize data to JSON
        json_data = json.dumps(result)
        if os.getenv("ENVIRONMENT") == "development":
            print(f'Function {inspect.currentframe().f_code.co_name} returns: {json_data}')
        return func.HttpResponse(
            body=json_data,
            mimetype="application/json",
            status_code=500)    

@app.route(route="expression_openai_definition", auth_level=func.AuthLevel.FUNCTION)
def expression_openai_definition(req: func.HttpRequest) -> func.HttpResponse:
    if os.getenv("ENVIRONMENT") == "development":
        print(f'HTTP trigger function {inspect.currentframe().f_code.co_name} processed a request.')
    else:
        logging.info(f'HTTP trigger function {inspect.currentframe().f_code.co_name} processed a request.')

    load_dotenv()

    expression = req.params.get('expression')
    if not expression:
        try:
            req_body = req.get_json()
            expression = req_body.get('expression')
        except ValueError:
            req_error = {'error' : 'Request failed due to missing parameter [expression]'}
            # Serialize data to JSON
            return func.HttpResponse(
                body=json.dumps(req_error),
                mimetype="application/json",
                status_code=200)
    
    openai_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT') 
    deployment_name = os.getenv('DEPLOYMENT_NAME')
    openai_key = os.getenv('AZURE_OPENAI_API_KEY')
    openai_version = os.getenv('AZURE_OPENAI_API_VERSION')
    openai_url = f'{openai_endpoint}openai/deployments/{deployment_name}/chat/completions?api-version={openai_version}&api-key={openai_key}'

    if ' ' in expression:
        prompt = f'Define the expression \'{expression}\' and list a few examples that use it.'
    else:
        prompt = f'Define the word \'{expression}\' and list a few examples that use it.'
       
    payload_str = '{"messages": [{"role": "user","content":"'
    payload_str += prompt
    payload_str += '"}],"temperature": 0.7,"top_p": 0.95,"frequency_penalty": 0,"presence_penalty": 0,"max_tokens": 800,"stop": "null"}'
    
    # Define the headers
    headers = {
        'Content-Type': 'application/json',  # This is a common header, replace as needed
        # 'Authorization': 'Bearer YOUR_TOKEN'  # Replace 'YOUR_TOKEN' with your token
    }

    try:
        response_text = asyncio.run(asyncpostreq(openai_url, headers=headers, payloadstr=payload_str,verb="post"))
        if os.getenv("ENVIRONMENT") == "development":
            print(f'Function {inspect.currentframe().f_code.co_name} returns: {response_text}')

        response_json = json.loads(response_text)
        openai_answer = response_json['choices'][0]['message']['content']
        
        # Serialize data to JSON
        json_data = json.dumps(openai_answer)
        if os.getenv("ENVIRONMENT") == "development":
            print(f'Function {inspect.currentframe().f_code.co_name} returns: {json_data}')
        return func.HttpResponse(
            body=json_data,
            mimetype="application/json",
            status_code=200)
    except Exception as e:
        err_json = {"error" : f'{e}'}
        if os.getenv("ENVIRONMENT") == "development":
            print(f'Function {inspect.currentframe().f_code.co_name} returns: {json.dumps(err_json)}')
        return func.HttpResponse(
            body=json.dumps(err_json),
            mimetype="application/json",
            status_code=200)

@app.route(route="word_stemming", auth_level=func.AuthLevel.FUNCTION)
def word_stemming(req: func.HttpRequest) -> func.HttpResponse:
    if os.getenv("ENVIRONMENT") == "development":
        print(f'HTTP trigger function {inspect.currentframe().f_code.co_name} processed a request.')
    else:
        logging.info(f'HTTP trigger function {inspect.currentframe().f_code.co_name} processed a request.')

    expression = req.params.get('expression')
    if not expression:
        try:
            req_body = req.get_json()
            expression = req_body.get('expression')
        except ValueError:
            req_error = {'error' : 'Request failed due to missing parameter [expression]'}
            # Serialize data to JSON
            return func.HttpResponse(
                body=json.dumps(req_error),
                mimetype="application/json",
                status_code=200)
    
    # check if expression is a real expression (i.e. set of words) where stemming is not applicable 
    if len(expression.split(' ')) > 1:
        req_error = {'error' : 'Stemming is not applicable to an expression.'}
        # Serialize data to JSON
        return func.HttpResponse(
            body=json.dumps(req_error),
            mimetype="application/json",
            status_code=200)

    ps = PorterStemmer()
    word_stem = {'stem' : ps.stem(expression)}

    # Serialize data to JSON
    json_data = json.dumps(word_stem)
    if os.getenv("ENVIRONMENT") == "development":
        print(f'Function returns: {json_data}')
    return func.HttpResponse(
        body=json_data,
        mimetype="application/json",
        status_code=200)

@app.route(route="vocabulary_entries_count", auth_level=func.AuthLevel.FUNCTION)
def vocabulary_entries_count(req: func.HttpRequest) -> func.HttpResponse:
    if os.getenv("ENVIRONMENT") == "development":
        print(f'HTTP trigger function {inspect.currentframe().f_code.co_name} processed a request.')
    else:
        logging.info(f'HTTP trigger function {inspect.currentframe().f_code.co_name} processed a request.')
    
    with open('data/VOCABULARY.csv', 'r') as file:
        
        words_no = 0
        expressions_no = 0
        
        # Create a CSV reader
        reader = csv.reader(file)
            
        # Loop over each row in the file
        skipfirst = True
        for row in reader:
            if skipfirst:
                skipfirst = False
                continue
            if ' ' in row[0]:
                expressions_no = expressions_no + 1
            else:
                words_no = words_no + 1

    # Serialize data to JSON
    return func.HttpResponse(
        body=json.dumps({'word_count' : words_no, 'expression_count' : expressions_no, 'total_entries' : words_no + expressions_no}),
        mimetype="application/json",
        status_code=200)

@app.route(route="calculate_similarity", auth_level=func.AuthLevel.FUNCTION)
def calculate_similarity(req: func.HttpRequest) -> func.HttpResponse:
    if os.getenv("ENVIRONMENT") == "development":
        print(f'HTTP trigger function {inspect.currentframe().f_code.co_name} processed a request.')
    else:
        logging.info(f'HTTP trigger function {inspect.currentframe().f_code.co_name} processed a request.')

    try:
        req_body = req.get_json()
        userDefinition = req_body.get('user_definition')
        dictDefinition = req_body.get('dictionary_definition')
        openaiDefinition = req_body.get('openai_definition')
    except ValueError:
        req_error = {"error" : 'Request failed due to missing parameters [expression OR user_answer]'}
        # Serialize data to JSON
        return func.HttpResponse(
            body=json.dumps(req_error),
            mimetype="application/json",
            status_code=200)

    if userDefinition == '':
        return func.HttpResponse(
        body='Missing user definition.',
        mimetype="application/json",
        status_code=500)

    # calculate dictionary similarity score
    dictSimilarity = get_similarity_score(userDefinition,dictDefinition)

    # calculate OpenAI similarity score
    openAiSimilarity = get_similarity_score(userDefinition,openaiDefinition)
    
    scores = {"dicSimilarity": round(dictSimilarity,2), "openAiSimilarity" : round(openAiSimilarity,2)}

    # Serialize data to JSON
    json_data = json.dumps(scores)
    if os.getenv("ENVIRONMENT") == "development":
        print(f'Function returns: {json_data}')
    return func.HttpResponse(
        body=json_data,
        mimetype="application/json",
        status_code=200)
