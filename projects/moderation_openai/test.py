# from openai import OpenAI

# client = OpenAI()
# response = client.moderations.create(
#     model="omni-moderation-latest",
#     input=[
#         {"type": "text", "text": "moderations"},
#         {
#             "type": "image_url",
#             "image_url": {
#                 "url": "https://tw.portal-pokemon.com/play/resources/pokedex/img/pm/2b3f6ff00db7a1efae21d85cfb8995eaff2da8d8.png",
#             }
#         },
#     ],
# )

# result = response.results[0]
# print(result)

import time
import openai
from openai import OpenAI
from openai._exceptions import RateLimitError
client = OpenAI()

def safe_moderation_request(payload, retries=3, delay=2):
    for attempt in range(retries):
        try:
            return client.moderations.create(**payload)
        except RateLimitError:
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                raise

payload = {
    "model": "omni-moderation-latest",
    "input": [
        {"type": "text", "text": "moderations"},
        {
            "type": "image_url",
            "image_url": {
                "url": "https://tw.portal-pokemon.com/play/resources/pokedex/img/pm/2b3f6ff00db7a1efae21d85cfb8995eaff2da8d8.png",
            }
        },
    ],
}

response = safe_moderation_request(payload)
print(response.results[0])

