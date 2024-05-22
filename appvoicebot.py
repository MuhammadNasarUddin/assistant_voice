from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse
import openai
from newvoicebot import Voice_call_bot



app = Flask(__name__)

bot = Voice_call_bot()



@app.route("/voice", methods=["POST, GET"])
def voice():
    response = VoiceResponse()
    # Get the user's speech from the request
    if 'speech' in request.values:
        # Get the user's speech from the request
        user_speech = request.values['speech']
        # Send the user's speech to the bot
        bot_response = bot.user_chat(user_speech)
        # Respond to the user with the bot's response
        response.say(bot_response, voice='alice')
    else:
        response.say("Hello, how can I help you today?", voice='alice')
        response.listen()
    return str(response)


if __name__ == "__main__":
    app.run(debug=True)