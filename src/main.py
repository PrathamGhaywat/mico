from flask import Flask, request
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from openai import OpenAI
from dotenv import load_dotenv
import os
import logging


load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN") or ""
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET") or ""
AI_BASE_URL = os.getenv("AI_BASE_URL") or ""          
AI_API_KEY = os.getenv("AI_API_KEY") or ""      
AI_MODEL_ID = os.getenv("AI_MODEL_ID") or ""


logging.basicConfig(level=logging.INFO)


app = App(
    token=SLACK_BOT_TOKEN,
    signing_secret=SLACK_SIGNING_SECRET
)
handler = SlackRequestHandler(app)

client = OpenAI(base_url=AI_BASE_URL, api_key=AI_API_KEY)


@app.event("app_mention")
def handle_app_mention_events(body, say, logger):
    event = body.get("event", {})
    user = event.get("user")
    text = event.get("text", "")

    logger.info(f"App mentioned by {user}: {text}")

    try:
        completion = client.chat.completions.create(
            model=AI_MODEL_ID,
            messages=[
                {"role": "user", "content": f"Here is a Slack message, answer like a 10x time waster: {text}"}
            ]
        )
        response_text = completion.choices[0].message.content
        say(response_text)

    except Exception as e:
        logger.error(f"OpenAI error: {e}")
        say("Message so dumb, I failed to respond")

@app.message("hello")
def handle_hello(message, say, logger):
    user = message.get("user")
    text = message.get("text", "")

    logger.info(f"Received message from {user}: {text}")

    try:
        completion = client.chat.completions.create(
            model=AI_MODEL_ID,
            messages=[
                {"role": "user", "content": f"Here is a Slack message, answer like a 10x time waster: {text}"}
            ]
        )

        response_text = completion.choices[0].message.content
        say(response_text)

    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        say("Dumb message - my eyes got cance reading this")

flask_app = Flask(__name__)

@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

if __name__ == "__main__":
    logging.info("Starting Slack bot...")
    flask_app.run(port=3000)