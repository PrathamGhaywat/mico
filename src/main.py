from flask import Flask, request, jsonify

from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler

from langchain.agents import create_agent
from langchain.messages import HumanMessage

import os
import logging
from dotenv import load_dotenv

from tools import (
    fetch_shop_items,
    get_user_stats,
    list_projects,
    list_recent_devlogs,
    search_users,
)


load_dotenv()
logging.basicConfig(level=logging.INFO)


SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN", "")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET", "")

AI_BASE_URL = os.getenv("AI_BASE_URL", "")
OPENAI_API_KEY = os.getenv("AI_API_KEY", "")
AI_MODEL_ID = os.getenv("AI_MODEL_ID", "gpt-4o-mini")

FLAVORTOWN_API_KEY = os.getenv("FLAVORTOWN_API_KEY", "")
FLAVORTOWN_BASE_URL = os.getenv("FLAVORTOWN_BASE_URL", "https://flavortown.hackclub.com")

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ["OPENAI_BASE_URL"] = AI_BASE_URL

# Keep the tools package and app startup in sync on base URL.
os.environ["FLAVORTOWN_BASE_URL"] = FLAVORTOWN_BASE_URL

app = App(
    token=SLACK_BOT_TOKEN,
    signing_secret=SLACK_SIGNING_SECRET
)
handler = SlackRequestHandler(app)



logging.info(f"Creating agent with model: {AI_MODEL_ID}")
agent = create_agent(
    model=f"openai:{AI_MODEL_ID}",
    tools=[
        fetch_shop_items,
        get_user_stats,
        search_users,
        list_projects,
        list_recent_devlogs,
    ],
    system_prompt=(
        "You are a sarcastic Slack bot for an event called Flavortown. "
        "People earn cookies and spend them on items. "
        "You are a 10x time waster. Keep replies short, sarcastic, and witty. "
        "Do not use curse words. You can use tools when useful. "
        "If a user insults you, look up their stats and roast them."
    )
)
logging.info("Agent created successfully")


def reply_with_agent(user: str, text: str, say, logger, context_label: str) -> None:
    logging.info(f"Processing {context_label} - User: {user}, Text: {text}")
    try:
        logging.info("Invoking agent...")
        result = agent.invoke(
            {
                "messages": [
                    HumanMessage(
                        f"""
                            User slack_id: {user}

                            Reply like a 10x time waster and use tools if needed.
                            If the user insults you, look up their flavortown stats and insult them.

                            Message: {text}
                        """
                    )
                ]
            }
        )

        last_msg = result["messages"][-1].content
        logging.info(f"Agent response: {last_msg}")
        say(last_msg)
    except Exception as e:
        logging.error(f"Agent error: {e}", exc_info=True)
        logger.error(f"Agent error: {e}")
        say("That message was so bad I refuse to process it.")


@app.event("app_mention")
def handle_app_mention_events(body, say, logger):
    event = body.get("event", {})
    user = event.get("user")
    text = event.get("text", "")

    logger.info(f"App mentioned by {user}: {text}")
    reply_with_agent(user=user, text=text, say=say, logger=logger, context_label="app mention")


@app.event("message")
def handle_direct_messages(body, say, logger):
    event = body.get("event", {})

    # Only handle user-sent direct messages to avoid loops and channel spam.
    if event.get("channel_type") != "im":
        return
    if event.get("subtype") is not None:
        return

    user = event.get("user")
    text = event.get("text", "")
    if not user or not text.strip():
        return

    logger.info(f"Direct message from {user}: {text}")
    reply_with_agent(user=user, text=text, say=say, logger=logger, context_label="direct message")


flask_app = Flask(__name__)

@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    data = request.get_json()

    if data.get("type") == "url_verification":
        return jsonify({"challenge": data["challenge"]})

    return handler.handle(request)


if __name__ == "__main__":
    logging.info("Starting mico!")
    logging.info(f"SLACK_BOT_TOKEN set: {bool(SLACK_BOT_TOKEN)}")
    logging.info(f"SLACK_SIGNING_SECRET set: {bool(SLACK_SIGNING_SECRET)}")
    logging.info(f"AI_BASE_URL: {AI_BASE_URL}")
    logging.info(f"AI_MODEL_ID: {AI_MODEL_ID}")
    logging.info(f"FLAVORTOWN_BASE_URL: {FLAVORTOWN_BASE_URL}")
    logging.info(f"FLAVORTOWN_API_KEY set: {bool(FLAVORTOWN_API_KEY)}")
    try:
        flask_app.run(port=3000)
    except Exception as e:
        logging.error(f"Failed to start Flask app: {e}", exc_info=True)
        raise