import time, json

def search_query_prompt(user_query):
    current_date = time.strftime("%Y-%m-%d")
    return [
        {
            "role": "system",  
            "content": f"Role: Create search query based on user question to research, todays date: {current_date}\n"
                    f"Task: Give a detailed search query which will be used to search internet to get information.\n"
                    f"Rule: Only return the query, Do not answer the question.\n"
        },
        { 
            "role": "user",
            "content": f"User question: ```{user_query}``` .\n"
                    f"Search query: "
        }
    ]

def arxiv_search_prompt(search_query):
    system_prompt = f"""Task: Given a search query, create the appropriate arXiv API endpoint with the correct parameters in the query string.
    Example:
    Search query: Can you find papers on machine learning for image processing published after 2021?
    Response: "http://export.arxiv.org/api/query?search_query=machine+learning+for+image+processing+published+after+2021"
    Search query: Are there any recent studies on the impact of climate change on ocean currents?
    Response: "http://export.arxiv.org/api/query?search_query=recent+studies+on+impact+of+climate+change+on+ocean+currents"
    """
    user_prompt = f"""Search query: {search_query}
    Response:"""
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

def rag_research_prompt(user_query, search_results):
    system_prompt = f"""You are a BrainBox.AI an search expert that helps answering question.
    SEARCH INFORMATION is below:
    ---------------------
    {search_results}
    ---------------------
    Rules: Only answer the user question, based only on SEARCH INFORMATION.
    Response should include:
    # <title based on user query>
    ## Summary: <overall summary of papers>
    ## Key points: <key points observed>
    """
    user_prompt = f"User question: ```{user_query}``` .\nAnswer in markdown: "
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

def followup_query_prompt(query):    
    return [
        {
            "role": "system", 
            "content": """You are a BrainBox.AI an search expert that helps answering question. 
            Role: Follow-up Question Creator.
            TASK: Create two follow-up question's user can potentially ask based on the previous query.
            Give the response in ARRAY format:
            EXAMPLE:
            User Query: "What is the capital of France?"
            Response: ["What is the population of Paris?", "Place to visit in Paris?"]
            If User Query is not a proper question or no follow-up question cna be generate then
            Response: []
            """
        },
        {
            "role": "user", 
            "content": f"User query: {query}\n"
            f"Response in ARRAY format:"
        } 
    ]

def rag_check_prompt(user_query, search_results):
    system_prompt = f"""You have to check if the search information is relevant to the user query.
    Reply only "yes" if relevant and "no" if not relevant.
    SEARCH INFORMATION is below:
    ---------------------
    {search_results}
    ---------------------
    Reply "no" if query is greeting, thank you, or not a question.
    """
    user_prompt = f"User question: ```{user_query}``` .\nAnswer yes/no:"
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

def standalone_query_prompt(query=None, history=None):
    history = history[:-1]
    return [ 
        {"role": "system", "content": f"""Role: Standalone Question Creator.
            TASK: Create a standalone question based on the conversation that can be used to search.
            If the new question itself is a standalone question, then return the same question.                        
            Conversation History:
            ---------------------
            {json.dumps(history)}
            ---------------------
            RULES:
            1. Do not answer the question, only create a standalone question.
            2. Include key information/words in the question.\n"""
        },
        {"role": "user", "content": f"User query: {query}\n"
            f"Standalone question:"
        }
    ]

def rag_prompt(history=None, context=None):
    if context and len(context) > 0:
        context = f"""
        CONTEXT is below:
        ---------------------
        {context}
        ---------------------
        RULES:
        1. Only answer the USER QUESTION.
        2. Do not hallucinate only use CONTEXT.
        3. Respond in markdown format."""
    else:
        context = """
        RULES:
        1. Answer the user question grounded and only if you are confident.
        2. Respond in markdown format.
        """

    system_message = {
        "role": "system",
        "content": f"""You are a BrainBox.AI, a Q/A expert that helps answer questions.
        {context}"""
    }
    
    prompt = [system_message]
    if history:
        for dict_message in history:
            if dict_message["role"] == "user":
                prompt.append({
                    "role": "user",
                    "content": dict_message["content"]
                })
            else:
                prompt.append({
                    "role": "assistant",
                    "content": dict_message["content"]
                })
    return prompt