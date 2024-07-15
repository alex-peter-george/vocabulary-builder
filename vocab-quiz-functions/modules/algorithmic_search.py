# from sentence_transformers import util
import numpy as np
from modules.text_processing import generate_embeddings, embed_arb_datset
# from sklearn.metrics.pairwise import cosine_similarity

# def cosine_similarity_tf(model, query, txtcoll):
#     embedding_q = model.encode(query)
#     embedding_t = model.encode(txtcoll)
#     similarities = util.pytorch_cos_sim(embedding_q, embedding_t)
#     return similarities.tolist()[0]

# def cosine_similarity_tf2(e_query, e_txtcoll):
#     similarities = util.pytorch_cos_sim(e_query, e_txtcoll)
#     return similarities.tolist()[0]

# def cosine_similarity_sk(a, b):
#     return cosine_similarity([a],[b])[0][0]

def cosine_similarity_np(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def search_docs_numpy(dataset_doc, user_query, top_n):
    e_query = generate_embeddings(
        user_query,
        model="text-embedding-ada-deployment" # model should be set to the deployment name you chose when you deployed the text-embedding-ada-002 (Version 2) model
    )
    df_arbdocs = embed_arb_datset(dataset_doc)
    df_arbdocs["similarities"] = df_arbdocs.ada_v2.apply(lambda e_content: cosine_similarity_np(e_content, e_query))

    res = (
        df_arbdocs.sort_values("similarities", ascending=False)
        .head(top_n)
    )

    search_result = []
    for i in range(0,3):
        result0A = f'Answer'
        result0B = f'{res["Summary"][res.index[i]]}'
        result1A = f'Similarity'
        result1B = f'{res["similarities"][res.index[i]]*100:.2f}'
        result2A = 'DocumentTitle'
        result2B = f'{res["ArbTitle"][res.index[i]]}'
        result3A = 'DocumentID'
        result3B = f'{res["DocumentId"][res.index[i]]}'
        result4A = 'DocumentURL'
        result4B = f'{res["URL"][res.index[i]]}'
        result = {result0A: result0B,result1A : result1B,result2A : result2B,result3A : result3B,result4A : result4B}

        search_result.append(result)
   
    return search_result

