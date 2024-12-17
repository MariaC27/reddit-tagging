# reddit data collection & tagging

### description:
* Uses reddit API to get reddit post & comment data related to a specified search term. Gets all posts and comment threads containing the search term 
within the past 2 years in the specificed subreddits. Stores data in a json file initially, then writes to csv table to be joined with tagging data.

* Calls OpenAI api to generate list of 12 relevant sentiment tags according to the json data. Stores the tags in a csv file.
  
* For each tag and each post or comment object in the json, calls the OpenAI api to determine whether the tag applies to the post/comment (true/false). Generates
a CSV file with the post/comment id and tag.

Result will be a json file with data pulled from api, csv table with the 12 generated tags, a csv table with data about each post, and a csv table with post/comment id and associated tag. The last two csv tables can be joined on the id column and used for analysis or visualization.


### to run:
* Start venv, pip install -r requirements.txt, python script/script_name.py
* Run scripts in order (1-3). may need to move data files around or adjust paths. needs reddit client info and open ai api key in .env file
