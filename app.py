import os
import logging
import openai
from flask import Flask, redirect, render_template, request, url_for, session

logging.basicConfig(level=logging.DEBUG)


app = Flask(__name__)
openai.api_key = os.environ.get("OPENAI_API_KEY")
app.secret_key = "my_secret_key"

@app.route('/')
def index():
    # Retrieve the conversations list from the session
    if 'conversations' not in session:
        session['conversations'] = []
    conversations = session['conversations']
    logging.debug(f"The current conversation in the session: {conversations}")
    return render_template('index.html', conversations=conversations)

@app.route("/chatbot", methods=["POST"])
def chatbot():
    # Retrieve the conversations list from the session
    if 'conversations' not in session:
        session['conversations'] = []
    conversations = session['conversations']
    logging.debug(f"The request form: {request.get_json()}")
    data = request.get_json()
    message = data['message']
    
    # Append the current conversation to the list of previous conversations
    # See below for examples
    conversations.append(f"User: {message}")
    
    # Generate the prompt
    """ The prompt variable should contain the previous conversations to have context.
    We are inserting a newline character between each element from the conversations list 
    and also include the string "Bot: ", which tells the OpenAI API that the chatbot should generate a response.
    See below for examples.
    """
    previous_conversations = "\n".join(conversations) # + "\nBot: "
    instructions = get_instructions()
    prompt = f"{instructions}\n{previous_conversations}\nBot: "
    model = "text-davinci-003"
    completions = openai.Completion.create(engine=model, prompt=prompt, max_tokens=1024, n=1,stop=None,temperature=0.5)
    response = completions.choices[0].text.strip()
    if response:
        logging.debug(f"We made a API call and got this response: {response}")

    # Append the chatbot's response to the list of previous conversations
    conversations.append(f"Bot: {response}")
    
    return response

def get_instructions():
    return """
    Instructions:
    - Give answers to questions or help with issues. Be very polite.

    Examples:
    - Question: Where do I find the logs?
    - Answer: If you use the app there is a log file called specterApp.log in the SPECTER_DATA_FOLDER in your user directory.
    - Issue: I can't connect to my node.
    - Answer: Run the connection test in the app. And tell me what it says. In any case, check that your RPC credentials are correct. 
    - Question: Devices and wallets? What is the difference?
    - Answer: The logic is that devices store keys, and you can combine these keys in different wallets like multisig or singlesig. 
    """


# Examples of how the data structures look like
"""
conversations = [
    "User: How are you?",
    "Bot: I'm doing well, thank you! How are you?",
    "User: I'm doing good, thanks. Do you know the weather today?",
    "Bot: It looks like it's going to be a nice day today! The weather forecast says it will be sunny and warm."
]

previous_conversations = 
"User: How are you?\nBot: I'm doing well, thank you! How are you?\nUser: I'm doing good, thanks. Do you know the weather today?\nBot: It looks like it's going to be a nice day today! The weather forecast says it will be sunny and warm."

API response
{
  "id": "27e1a3c3-3d7b-4474-abf7-9d9e2b1b10c6",
  "model": "text-davinci-003",
  "prompt": "User: How are you?\nBot: I'm doing well, thank you! How are you?\nUser: I'm doing good, thanks. Do you know the weather today?\nBot: It looks like it's going to be a nice day today! The weather forecast says it will be sunny and warm.\nBot: ",
  "choices": [
    {
      "text": "It sounds like you're having a good day. Is there anything else you'd like to chat about?",
      "index": 0,
      "logprobs": null
    }
  ],
  "created": "2022-12-18T23:22:53.763553Z",
  "updated": "2022-12-18T23:22:53.776565Z"
}

The choices field in the completions variable is a list because the OpenAI API allows you to request multiple potential responses to a prompt 
by specifying the n parameter in the openai.Completion.create() method. 
For example, if you set n=2, the API will return a list of two potential responses in the choices field.

"""
