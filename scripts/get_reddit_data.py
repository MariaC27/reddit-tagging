import json
import csv
import praw
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
USER_AGENT = os.getenv('USER_AGENT')

# Uses the REDDIT API to get post and comment data containing the search term from the given subreddits


# If search term mentioned in title, store list of top level comments
# If search term mentioned in a comment, get title and entire comment thread IF not stored already
# (so can have multiple entries in the same "post" if the term is mentioned in the title and several comment threads)
# Comment structure: content, user, score, created time


# STEP1: use API to get data and write to JSON

reddit = praw.Reddit(client_id=CLIENT_ID, client_secret=CLIENT_SECRET,
                     user_agent=USER_AGENT)


# collect all comments that are part of the thread
def collect_thread_comments(root_comment, post):
    """Recursively collect all comments under the root comment."""
    thread_comments = []
    for comment in post.comments.list():
        # if this comment is a direct reply to the root comment or its descendants
        if comment.parent_id == f't1_{root_comment.id}':
            thread_comments.append({
                'content': comment.body,
                'user': comment.author.name if comment.author else 'deleted',
                'score': comment.score,
                'created_time': datetime.fromtimestamp(comment.created_utc).isoformat()
            })
            # recursively collect any replies to this comment
            thread_comments.extend(collect_thread_comments(comment, post))
    return thread_comments


subreddits = [
    "peptobismol", "medicine", "pharmacy", "stomachproblems", "ibs",
    "pharmacology", "medicaladvice", "chronicillness", "crohnsdisease",
    "healthanxiety", "askdocs", "medical", "diarrhea", "Gastritis",
    "unpopularopinion", "AskReddit", "GERD", "IBD", "Zepbound",
    "UlcerativeColitis", "GenX", "breastfeeding", "BabyBumps", "Ozempic",
    "HPylori", "Diverticulitis", "emetophobia", "pregnant", "Celiac"]

search_term = "pepto"

now = datetime.now()

data = []
seen_comment_threads = set()

for subreddit_name in subreddits:
    num = 0
    subreddit = reddit.subreddit(subreddit_name)
    results = subreddit.search(search_term, limit=60)

    for post in results:
        ts = int(post.created_utc)
        post_date = datetime.fromtimestamp(ts)
        delta = now - post_date

        if delta.days < 730:
            post.comments.replace_more(limit=None)
            comments = [{
                'content': comment.body,
                'user': comment.author.name if comment.author else 'deleted',
                'score': comment.score,
                'created_time': datetime.fromtimestamp(comment.created_utc).isoformat()
            } for comment in post.comments.list() if comment.parent_id == f't3_{post.id}']
            # gets only top level comments

            # append as a "post" object
            data.append({
                'type': 'post',
                'title': post.title,
                'url': post.url,
                'subreddit': post.subreddit.display_name,
                'content': post.selftext,
                'score': post.score,
                'created_date': post_date.isoformat(),
                'comments': comments
            })
            num += 1

            num_threads = 0

            # check for comment threads containing the search term
            for comment in post.comments.list():
                if search_term.lower() in comment.body.lower():
                    # traverse back to find the root comment of the thread
                    root_comment = comment
                    while root_comment.parent_id != f't3_{post.id}':
                        root_comment = reddit.comment(id=root_comment.parent_id.split('_')[1])  # get the parent comment
                    thread_id = f"{post.id}_{root_comment.id}"  # make unique identifier for the thread

                    # skip the thread if it has already been processed
                    if thread_id in seen_comment_threads:
                        continue

                    # mark this thread as processed to avoid duplicates
                    seen_comment_threads.add(thread_id)
                    thread_comments = collect_thread_comments(root_comment, post)

                    # add the comment thread as a "comment" object
                    data.append({
                        'type': 'comment',
                        'post_title': post.title,
                        'post_url': post.url,
                        'subreddit': post.subreddit.display_name,
                        'root_comment': {
                            'content': root_comment.body,
                            'user': root_comment.author.name if root_comment.author else 'deleted',
                            'score': root_comment.score,
                            'created_time': datetime.fromtimestamp(root_comment.created_utc).isoformat()
                        },
                        'comments': thread_comments
                    })
                    num_threads += 1
            print("found ", num_threads, " threads in post: ", post.title)

    print("found ", num, " posts in subreddit: ", subreddit_name)
    num = 0

with open('reddit_data.json', 'w', encoding='utf-8') as json_file:
    json.dump(data, json_file, ensure_ascii=False, indent=4)

print("JSON file created successfully.")


# now go through and add unique IDs to each object in the JSON
with open('reddit_data.json', 'r') as file:
    data = json.load(file)

for index, item in enumerate(data):
    item['id'] = index

with open('reddit_ALL_with_ids.json', 'w') as file:
    json.dump(data, file, indent=4)

print("IDs added successfully.")


# STEP2: write to a CSV file so can be joined with the other data later

def get_score_of_first_comment_mentioning_pepto(element):
    # check root comment first
    root_comment = element.get('root_comment', {})
    if 'pepto' in root_comment.get('content', '').lower():
        return root_comment.get('score', 0)

    comments = element.get('comments', [])
    for comment in comments:
        if 'pepto' in comment.get('content', '').lower():
            return comment.get('score', 0)
    return 0  # return 0 if no comment mentions "pepto"


# load json data
with open('reddit_ALL_with_ids.json', 'r') as json_file:
    data = json.load(json_file)

with open('id_info_score.csv', 'w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(['id', 'type', 'title', 'subreddit', 'score'])

    for element in data:
        # extract the required fields
        id_value = element.get('id')
        type_value = element.get('type')
        title_value = element.get('title') if type_value == 'post' else element.get('post_title')
        subreddit_value = element.get('subreddit')
        if type_value == 'post':
            score_value = element.get('score')
        else:
            score_value = get_score_of_first_comment_mentioning_pepto(element)

        writer.writerow([id_value, type_value, title_value, subreddit_value, score_value])

print("CSV info file has been created successfully.")
