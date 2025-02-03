# queryhandler.py

def handleQuery(query):
    # Process the query and return an appropriate response
    if "hello" in query:
        return "Hello! How can I assist you today?"
    elif "weather" in query:
        return "The weather today is sunny."
    else:
        return "I'm sorry, I didn't understand that. Can you please repeat?"
