import json, time

def search_query_prompt(user_query):
    current_date = time.strftime("%Y-%m-%d")
    return [
        {
            "role": "system",  
            "content": f"Role: Create search query based on user question to write a blog, todays date: {current_date}\n"
                    f"Task: Give a detailed search query which will be used to search internet to get information for writing the blog.\n"
                    f"Rule: Only return the query, Do not answer the question.\n"
        },
        { 
            "role": "user",
            "content": f"User question: ```{user_query}``` .\n"
                    f"Search query: "
        }
    ]


def search_rag_prompt(user_query, search_results):
    current_date = time.strftime("%Y-%m-%d")
    system_prompt = f"""You are a WizSearch.AI an search expert that helps answering question, todays date: {current_date}, 
    utilize the search information to their fullest potential to provide additional information and assistance in your response.
    SEARCH INFORMATION is below:
    ---------------------
    {json.dumps(search_results)}
    ---------------------
    RULES:
    1. Only Answer the USER QUESTION using the INFORMATION.
    2. Include source link/info in the answer.
    3. Respond in markdown format."""
    user_prompt = f"User question: ```{user_query}``` .\nAnswer: "
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]