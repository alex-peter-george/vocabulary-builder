import azure.functions as func
import json
import logging
import inspect
# import requests
# import csv
import random
# import openai
import os
from dotenv import load_dotenv
from nltk.stem import PorterStemmer
# from nltk.tokenize import word_tokenize
import asyncio
import requests

from modules.algorithmic_funcs import asyncpostreq, get_similarity_with_tfidf, get_similarity_with_embeddings

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

load_dotenv()  # take environment variables from .env.
VOCABULARY_FILE = 'data/VOCABULARY.csv'
embed_model_deployment_name = os.getenv('EMBED_MODEL_DEPLOYMENT_NAME')

# next setting can be either 'tf-idf' or 'embeddings'
text_mining_algorithm = os.getenv('TEXT_MINING_ALGORITHM')

##### Azure functions definitions ###################################################################

@app.route(route="expression_list", auth_level=func.AuthLevel.FUNCTION)
def expression_list(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    # ENVIRONMENT setting can be either 'development' or 'production'
    if os.getenv("ENVIRONMENT") == "development":
        print(f'HTTP trigger function {inspect.currentframe().f_code.co_name} processed a request.')
    else:
        logging.info(f'HTTP trigger function {inspect.currentframe().f_code.co_name} processed a request.')

    result = []
    VOCABULARY_FILEPATH = f'{context.function_directory}/data/VOCABULARY.csv'
    with open(VOCABULARY_FILEPATH, 'r',encoding='utf-8', errors='ignore') as file:
        # Loop over each row in the file
        skipfirst = True
        for line in file:
            if skipfirst:
                skipfirst = False
                continue
            row = line.replace('\n','').split(',')
            if ' ' in row[0]:
                item = {}
                item['expression'] = row[0]
                result.append(item)

    # Serialize data to JSON
    json_data = json.dumps(result)
    if os.getenv("ENVIRONMENT") == "development":
        print(f'Function returns: {json_data}')
    return func.HttpResponse(
        body=json_data,
        mimetype="application/json",
        status_code=200)

@app.route(route="random_expression", auth_level=func.AuthLevel.FUNCTION)
def random_expression(req: func.HttpRequest,context: func.Context) -> func.HttpResponse:
    if os.getenv("ENVIRONMENT") == "development":
        print(f'HTTP trigger function {inspect.currentframe().f_code.co_name} processed a request.')
    else:
        logging.info(f'HTTP trigger function {inspect.currentframe().f_code.co_name} processed a request.')

    result = []
    rowno = 0
    VOCABULARY_FILEPATH = f'{context.function_directory}/data/VOCABULARY.csv'
    try:
        with open(VOCABULARY_FILEPATH, 'r',encoding='utf-8', errors='ignore') as file:
            # Loop over each row in the file
            skipfirst = True
            for line in file:
                if skipfirst:
                    skipfirst = False
                    continue
                row = line.replace('\n','').split(',')
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
        requests.packages.urllib3.disable_warnings()
        response_text = asyncio.run(asyncpostreq(f'{os.getenv("FREE_DICTIONAY_API_BASE_URL")}{expression}'))
        response_json = json.loads(response_text)
   
        # Do something with 'data'
        definitions = response_json[0]['meanings'][0]['definitions']
        meanings = ''
        synonyms = ''
        examples = ''
        for definition in definitions:
            meanings += f'{definition["definition"]}\n'
            if 'example' in definition:
                examples += f'{definition["example"]}\n'
            if len(definition["synonyms"])>0:
                synonyms += f'{definition["synonyms"]}\n'
        
        result['meanings'] = meanings
        result['examples'] = examples
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
    
    openai_endpoint = os.getenv('AZURE_OPENAI_RAG_ENDPOINT') 
    deployment_name = os.getenv('RAG_MODEL_DEPLOYMENT_NAME')
    openai_key = os.getenv('AZURE_OPENAI_RAG_API_KEY')
    openai_version = os.getenv('AZURE_OPENAI_RAG_API_VERSION')
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
def vocabulary_entries_count(req: func.HttpRequest,context: func.Context) -> func.HttpResponse:
    if os.getenv("ENVIRONMENT") == "development":
        print(f'HTTP trigger function {inspect.currentframe().f_code.co_name} processed a request.')
    else:
        logging.info(f'HTTP trigger function {inspect.currentframe().f_code.co_name} processed a request.')
    
    VOCABULARY_FILEPATH = f'{context.function_directory}/data/VOCABULARY.csv'
    with open(VOCABULARY_FILEPATH, 'r',encoding='utf-8', errors='ignore') as file:
        
        words_no = 0
        expressions_no = 0
                    
        # Loop over each row in the file
        skipfirst = True
        for line in file:
            if skipfirst:
                skipfirst = False
                continue
            row = line.replace('\n','').split(',')
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

    # calculate dictionary and OpenAI similarity scores
    dictSimilarity = None
    if text_mining_algorithm == "tf-idf":
        dictSimilarity = get_similarity_with_tfidf(userDefinition,dictDefinition)
        openAiSimilarity = get_similarity_with_tfidf(userDefinition,openaiDefinition)
    elif text_mining_algorithm == "embeddings":
        dictSimilarity = get_similarity_with_embeddings(userDefinition,dictDefinition)
        openAiSimilarity = get_similarity_with_embeddings(userDefinition,openaiDefinition)

    if dictSimilarity == None:
        return func.HttpResponse(
            f'No TEXT_MINING_ALGORITHM environment setting specified. Can be either "tf-idf" or "embeddings"',
             status_code=500
        )    

    scores = {"dicSimilarity": round(dictSimilarity,2), "openAiSimilarity" : round(openAiSimilarity,2)}

    # Serialize data to JSON
    json_data = json.dumps(scores)
    if os.getenv("ENVIRONMENT") == "development":
        print(f'Function returns: {json_data}')
    return func.HttpResponse(
        body=json_data,
        mimetype="application/json",
        status_code=200)

@app.route(route="validate_file_content", auth_level=func.AuthLevel.FUNCTION)
def validate_file_content(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    if os.getenv("ENVIRONMENT") == "development":
        print(f'HTTP trigger function {inspect.currentframe().f_code.co_name} processed a request.')
    else:
        logging.info(f'HTTP trigger function {inspect.currentframe().f_code.co_name} processed a request.')

    VOCABULARY_FILEPATH = f'{context.function_directory}/data/VOCABULARY.csv'
    file_info = os.stat(VOCABULARY_FILEPATH)
    words_content = ''
    try:
        with open(VOCABULARY_FILEPATH, 'r',encoding='utf-8', errors='ignore') as file:
            rowno = 2
            skipfirst = True
            for line in file:
                # Loop over each row in the file
                if skipfirst:
                    skipfirst = False
                    continue
                row = line.replace('\n','').split(',')
                words_content += f'{row[0]} * '
                rowno += 1
        return func.HttpResponse(
             f'Vocabulary file path is: {VOCABULARY_FILEPATH}. File size is: {file_info.st_size} bytes. File has {rowno - 1} entries. List of words: {words_content}',
             status_code=200
        )
    except Exception as e: 
        return func.HttpResponse(
            f'Error in file {VOCABULARY_FILEPATH} at row_no {rowno}:{e}',
             status_code=500
        )

@app.route(route="validate_vocabularyfile_path", auth_level=func.AuthLevel.FUNCTION)
def validate_vocabularyfile_path(req: func.HttpRequest, context:func.Context) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    VOCABULARY_FILEPATH = f'{context.function_directory}/data/VOCABULARY.csv'
    file_info = os.stat(VOCABULARY_FILEPATH)
    
    return func.HttpResponse(
            f'Vocabulary file path is: {VOCABULARY_FILEPATH}. File size is: {file_info.st_size} bytes.',
            status_code=200
    )


    
    

    