from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse
import os
import time
import re
from openai import OpenAI

class Voice_call_bot:
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.assistant_id = "asst_6l4Tm14nWBhyz2LXYqrOjk9z"

        # Update the assistant
        self.client.beta.assistants.update(
            self.assistant_id,
            name="Voice Bot Assistant",
            instructions="You are a voice bot Assistant. You can answer questions and provide information from the given files. Do not include the source of the file in the output.",
            model="gpt-4o",
            tools=[{"type": "file_search"}],
            tool_resources={
                "file_search": {
                    "vector_store_ids": ["vs_DlqjMCRS3fjfxcHGWTuiTQ6R"]
                }
            }
        )

    # Function to chat with the bot
    def user_chat(self, query):
        thread = self.client.beta.threads.create()

        # Send the user message
        self.client.beta.threads.messages.create(
            thread_id=thread.id,
            role='user',
            content=query
        )

        # Create a run
        run = self.client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=self.assistant_id,
            instructions=""
        )

        # Poll the run until it completes
        while True:
            run = self.client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            if run.status == 'completed':
                break
            time.sleep(1)

        # Retrieve the messages
        messages = self.client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id)
        messages_list = list(messages)
        messages_content = messages_list[0].content[0].text
        cleaned_text = re.sub('【.*?†.*】', '', messages_content.value)
        return cleaned_text

# Initialize Flask application
app = Flask(__name__)

# Initialize Voice_call_bot
voice_bot = Voice_call_bot()

@app.route("/voice", methods=['GET', 'POST'])
def voice():
    response = VoiceResponse()

    # Get the user's speech input from Twilio
    if 'SpeechResult' in request.values:
        user_speech = request.values['SpeechResult']
        # Send the user's speech to Voice_call_bot
        bot_response = voice_bot.user_chat(user_speech)
        # Respond back to the user
        response.say(bot_response)
    else:
        # Initial prompt
        response.say("Hello! How can I help you today?")
        response.listen()

    return str(response)

if __name__ == "__main__":
    app.run(debug=True)
