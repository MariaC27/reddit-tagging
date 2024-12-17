import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

OPEN_AI_KEY = os.getenv('OPEN_AI_KEY')

# call openai API to generate a list of tags based on the JSON data


client = OpenAI(api_key=OPEN_AI_KEY)


def make_api_request(text_input):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": (
                    f"""
                    See the following file in JSON format: {text_input}. This file has a list of objects of "post" and "comment" type from various subreddits that contain
                    references to "pepto" or "pepto bismol" or similar. Take 50 random samples of 30 items each and use these to generate "tags" of commonly used words or
                    phrases related to the sentiment and context surrounding pepto bismol discussions in these posts and comments. Return a list of these tags. Tags should
                    indicate sentiment in which pepto was discussed. Make sure to include both positive and negative sentiment and context. I want the actual output, not
                    a python script.
                    """
                )
            }
        ]
    )
    return response


with open('reddit_ALL_with_ids.json', 'r') as file:
    data = json.load(file)

text = json.dumps(data, indent=2)
result = make_api_request(text)

res = result.choices[0].message.content

print("res: ", res)
