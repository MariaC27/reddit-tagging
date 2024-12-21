import json
import csv
import vertexai
from vertexai.generative_models import GenerativeModel


PROJECT_ID = "noxu-dev-marias-team-e4a5f2"
vertexai.init(project=PROJECT_ID, location="us-central1")

# an alternative for the tagging if openai tokens are not enough


def make_gemini_request(text_input):

    model = GenerativeModel("gemini-1.5-pro")

    prompt = f"""
    See the following data in JSON format: {text_input}. This data has a list of objects of "post" and "comment" type from various subreddits that contain
    references to "tums" or similar. Take 50 random samples of 30 items each and use these to generate "tags" of commonly used words or
    phrases related to the sentiment and context surrounding the product in these posts and comments. Return a list of 12 of these tags. Tags should
    indicate sentiment in which the product was discussed. Make sure to include both positive and negative sentiment and context. I want the actual output, not
    a python script. Return ONLY the list of tags as a list of strings, nothing else because I want to write them to a csv file.
    """

    response = model.generate_content(prompt)
    return response


with open('private_data/tums_reddit_data.json', 'r') as file:
    data = json.load(file)

text = json.dumps(data, indent=2)
result = make_gemini_request(text)

res = result.text.strip("```json")

print(res)


# write tags to csv
with open('tums_tags.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['tag'])
    for tag in res:
        writer.writerow([tag])

print("Tags have been written to csv.")
