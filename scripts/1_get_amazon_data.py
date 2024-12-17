import json
import csv

# assumes we already have a json with the amazon data (scripts in another repo)
# now loading reviews from json data into a csv table so it can be joined with tagged data later

with open('amazon_data.json', 'r') as json_file:
    data = json.load(json_file)

with open('amazon_id_info.csv', 'w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(['id', 'product', 'review_title', 'rating'])

    for element in data:
        # extract the reviews
        product = element.get('title')
        asin = element.get('asin')

        # writer.writerow([title])

print("CSV info file has been created successfully.")
