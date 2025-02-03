from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values

# Load environment variables from .env file.
env_vars = dotenv_values(".env")

# Retreive specific environment variables for username,assistant name and API key.
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

#intialize the groq client using provided API key.
client = Groq(api_key=GroqAPIKey)

# intialize an empty list to store chat messages.
messages = []

#define a system message that providescontext to the AI chatbot.
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Telugu, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

# a list of system instructions for the chatbot.
SystemChatBot = [
    {"role": "system", "content": System}
]

# attempt to load the chat log from the JSON file.
try:
    with open(r"Data\Chatlog.json", "r") as f:
        messages = load(f)
except FileNotFoundError:
    # if the file does not exist, create it.
    with open(r"Data\Chatlog.json", "w") as f:
        dump([], f)

# function to get real time date and time.
def RealtimeInformation():
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%I")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")
    
    # format the information into a string.
    data = f"Please use this real-time information if needed,\n"
    data = f"Day: {day}\nDate: {date}\nMonth: {month}\nYear: {year}\n"
    data = f"Time: {hour} hours :{minute} minutes :{second} seconds.\n"
    return data

# function to modify the chatbot's response before formatting.
def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

# main chatbot function to handle user queries.
def ChatBot(Query):
    """ This function sends the user's query to the chatbot and returns the AI's response. """
    
    try:
        # load the existing chat log from JSON file.
        with open(r"Data\Chatlog.json", "r") as f:
            messages = load(f)
            
        # Append the user's query to the messages list.
        messages.append({"role": "user", "content": f"{Query}"})
        
        # make a request to the Groq API for response.
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )
        Answer = ""
        
        # process the streamed response chunks.
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content
                
        Answer = Answer.replace("</s>", "")
        
        # append the chatbot's responses to the messages list.
        messages.append({"role": "assistant", "content": Answer})
        
        # save the updated chat log to the JSON file.
        with open(r"Data\Chatlog.json", "w") as f:
            dump(messages, f, indent=4)
            
        # return the chatbot's response.
        return AnswerModifier(Answer=Answer)
    
    except Exception as e:
        #handle errors by printing the exception and resetting the chat log.
        print(f"Error: {e}")
        with open(r"Data\Chatlog.json", "w") as f:
            dump([], f, indent=4)
            return ChatBot(Query)
        
# main program entry point.
if __name__ == "__main__":
    while True:
        user_input = input("Enter your Question: ")
        print(ChatBot(user_input))