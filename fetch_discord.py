import requests

url = "https://community.supertokens.com/api/threads"
params = {
    "channelId": "ae164b95-2204-44d4-9595-69c1cdaf17ad",
    "accountId": "4e18cd5a-78d6-4be7-b53a-236bf4b40867"
}
headers = {
    "Content-Type": "application/json"
}

prev_cursor = None
while True:
    if prev_cursor is not None:
        params["cursor"] = prev_cursor
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    threads = data["threads"]
    for thread in threads:
        if len(thread["messages"]) <= 1:
            # this is cause previously, we used to not create threads for messages.
            continue
        # Do something with each thread
        for message in thread["messages"]:
            if (message["author"] is None or message["body"] is None):
                continue
            # Do something with each message
            print(message["author"]["username"] + ": " + message["body"])
            print()
        print("================= " + str(prev_cursor) + " =================")
    if data["nextCursor"] is None or data["nextCursor"]["prev"] is None:
        break
    prev_cursor = data["nextCursor"]["prev"]