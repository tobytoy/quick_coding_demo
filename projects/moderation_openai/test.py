from openai import OpenAI

image_url = ''
client = OpenAI()

response = client.moderations.create(
    model="omni-moderation-latest",
    input=[
        {"type": "text", "text": "moderations"},
        {
            "type": "image_url",
            "image_url": {
                "url": "https://tw.portal-pokemon.com/play/resources/pokedex/img/pm/2b3f6ff00db7a1efae21d85cfb8995eaff2da8d8.png",
            }
        },
    ],
)

result = response.results[0]

print(result)
