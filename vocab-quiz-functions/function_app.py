import azure.functions as func
import json
import logging
import inspect
import requests
import csv
import random
import openai
import os
from dotenv import load_dotenv
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

load_dotenv()  # take environment variables from .env.

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)
VOCABULARY_FILE = 'data/VOCABULARY.csv'

@app.route(route="expression_list")
def expression_list(req: func.HttpRequest) -> func.HttpResponse:
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
    return func.HttpResponse(
        body=json_data,
        mimetype="application/json",
        status_code=200)

@app.route(route="random_expression")
def random_expression(req: func.HttpRequest) -> func.HttpResponse:
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

    # Pick up random set from the array
    random_word = random.choice(result)

    # Serialize data to JSON
    json_data = json.dumps(random_word)
    return func.HttpResponse(
        body=json_data,
        mimetype="application/json",
        status_code=200)

@app.route(route="expression_dictionary_definition", auth_level=func.AuthLevel.FUNCTION)
def expression_dictionary_definition(req: func.HttpRequest) -> func.HttpResponse:
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
        

    # Make a GET request to the API
    response = requests.get(f'{os.getenv('FREE_DICTIONAY_API_BASE_URL')}{expression}',verify=False)

    # Check if the request was successful
    
    if response.status_code == 200:
        # Parse the response as JSON
        data = response.json()
        
        # Do something with 'data'
        definitions = data[0]['meanings'][0]['definitions']
        meanings = ''
        synonyms = ''
        for definition in definitions:
            meanings += f'{definition["definition"]}\n'
            synonyms += '\n'.join(definition["synonyms"])
        
        result['meanings'] = meanings
        result['synonyms'] = synonyms
    else:
        result['error'] = f'Request failed with status code {response.status_code}'

    # Serialize data to JSON
    json_data = json.dumps(result)
    return func.HttpResponse(
        body=json_data,
        mimetype="application/json",
        status_code=200)

@app.route(route="expression_openai_definition", auth_level=func.AuthLevel.FUNCTION)
def expression_openai_definition(req: func.HttpRequest) -> func.HttpResponse:
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
    
    openai.api_key = os.getenv('AZURE_OPENAI_API_KEY')
    openai.api_version = "2024-02-01"
    openai.azure_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')

    # Use the GPT-3 API to generate a summary
    response = openai.chat.completions.create(
        model="gpt-35-turbo",
        messages=[
                {"role": "system", "content": "You are a helpful assistant that provides meanings of an English language word or expression."},
                {"role": "user", "content": f"{expression}"},
            ],
    )
    meanings = response.choices[0].message.content
    
    # Serialize data to JSON
    json_data = json.dumps(meanings)
    return func.HttpResponse(
        body=json_data,
        mimetype="application/json",
        status_code=200)

@app.route(route="word_stemming", auth_level=func.AuthLevel.FUNCTION)
def word_stemming(req: func.HttpRequest) -> func.HttpResponse:
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
    return func.HttpResponse(
        body=json.dumps(word_stem),
        mimetype="application/json",
        status_code=200)

@app.route(route="calculate_similarity", auth_level=func.AuthLevel.FUNCTION)
def calculate_similarity(req: func.HttpRequest) -> func.HttpResponse:
    logging.info(f'HTTP trigger function {inspect.currentframe().f_code.co_name} processed a request.')

    try:
        req_body = req.get_json()
        expression = req_body.get('expression')
        userAnswer = req_body.get('user_answer')
    except ValueError:
        req_error = {"error" : 'Request failed due to missing parameters [expression OR user_answer]'}
        # Serialize data to JSON
        return func.HttpResponse(
            body=json.dumps(req_error),
            mimetype="application/json",
            status_code=200)

    # get dictionary answer
    dicAnswer = ''

    # get openAi answer
    openaiAnswer = ''

    # calculate dictionary similarity score
    dicSimilarity = 0.45

    # calculate OpenAI similarity score
    openAiSimilarity = 0.53
    
    scores = {"dicSimilarity": dicSimilarity, "openAiSimilarity" : openAiSimilarity}

    # Serialize data to JSON
    json_data = json.dumps(scores)
    return func.HttpResponse(
        body=json_data,
        mimetype="application/json",
        status_code=200)