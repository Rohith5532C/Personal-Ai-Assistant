from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import mtranslate as mt

# Load environment variables from .env file.
env_vars = dotenv_values(".env")
# get the input language settings from environment variables.
InputLanguage = env_vars.get("InputLanguage")

# define the HTML code for the speech recognition interface.
HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new webkitSpeechRecognition() || new SpeechRecognition();
            recognition.lang = '';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript;
            };

            recognition.onend = function() {
                recognition.start();
            };
            recognition.start();
        }

        function stopRecognition() {
            recognition.stop();
            output.innerHTML = "";
        }
    </script>
</body>
</html>'''

# replace the language settings in the HTML code.
HtmlCode = str(HtmlCode).replace("recognition.lang = '';", f"recognition.lang = '{InputLanguage}';")

# write the modified HTML code to the file.
with open(r"Data\Voice.html", "w") as f:
    f.write(HtmlCode)
    
# get the current working directory.
current_dir = os.getcwd()
# Generate the path to the HTML file.
Link = f"{current_dir}/Data/Voice.html"

# set the Chrome options for the selenium web driver.
chrome_options = Options()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.142.86 Safari/537.36"
chrome_options.add_argument(f'user-agent={user_agent}')
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
#chrome_options.add_argument("--headless=new")
#initialize the Chrome web driver using the ChromeDriverManager.
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# define the path for temporary files.
TempDirPath = rf"{current_dir}/Frontend/Files"

# function to set the assistant's status by writing it to a file.
def SetAssistantStatus(Status):
    with open(rf'{TempDirPath}/Status.data', "w", encoding='utf-8') as file:
        file.write(Status)
        
# function to modify a query to ensure proper punctuation and formatting.
def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "when", "where", "why", "who", "which", "whose", "whom"]
    
    # check if the query is a question add question mark.
    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.','?','!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        # add a peroid if query is not a question.
        if query_words[-1][-1] in ['.','?','!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."
            
    return new_query.capitalize()

# function to translate text into english using the mtranslate library.
def UniversalTranslator(Text):
    english_translation = mt.translate(Text, "en", "auto")
    return english_translation.capitalize()

# function to perform speech recognition using the selenium web driver.
def SpeechRecognition():
    # open the HTML file in the browser.
    driver.get("file:///" + Link)
    # start speech recognition by clicking the start button.
    driver.find_element(by=By.ID, value="start").click()
    
    while True:
        try:
            # get the recognized text from html.
            Text = driver.find_element(by=By.ID, value="output").text
            
            if Text:
                # stop recognition by clicking the stop button.
                driver.find_element(by=By.ID, value="end").click()
                
                # if the input language is english, return the modified query.
                if InputLanguage.lower() == "en" or "en" in InputLanguage.lower():
                    return QueryModifier(Text)
                else:
                    # if the input language is not english,translate the text and return it.
                    SetAssistantStatus("Translating...")
                    return QueryModifier(UniversalTranslator(Text))
                
        except Exception as e:
            pass
        
# main execution block.
if __name__ == "__main__":
    while True:
        # continously perfrm the speech recognition and print results.
        Text = SpeechRecognition()
        print(Text)