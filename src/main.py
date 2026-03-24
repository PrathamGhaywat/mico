from openai import OpenAI
from dotenv import load_dotenv
import os


load_dotenv()

AI_BASE_URL=os.getenv("AI_BASE_URL")
AI_API_KEY=os.getenv("AI_API_KEY")
AI_MODEL_ID=os.getenv("AI_MODEL_ID")


client = OpenAI(
          base_url=AI_BASE_URL,
            api_key=AI_API_KEY,

        )

completion = client.chat.completions.create(
          model=AI_MODEL_ID,
          messages=[
              {
                        "role": "user",
                              "content": "What is a good techstack for the year 2001?"

                  }

              ]

        )

print(completion.choices[0].message.content)

