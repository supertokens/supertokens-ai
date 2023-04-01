import requests
import json


# read existing threads from processed/discord_threads.json if it exists
try:
    with open("processed/discord_threads.json", "r") as f:
        threads = json.loads(f.read())
except:
    threads = []

def fetch_from_channel(channel):
    url = "https://community.supertokens.com/api/threads"
    params = {
        "channelId": channel,
        "accountId": "4e18cd5a-78d6-4be7-b53a-236bf4b40867"
    }
    headers = {
        "Content-Type": "application/json"
    }
    prev_cursor = None
    while True:
        if prev_cursor is not None:
            params["cursor"] = prev_cursor
        print("fetching threads with cursor: " + str(prev_cursor))
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        found_old_threads = False
        for thread in data["threads"]:
            if len(thread["messages"]) <= 1:
                # this is cause previously, we used to not create threads for messages.
                continue
            if thread["id"] in [t["id"] for t in threads]:
                found_old_threads = True
                continue
            threads.append(thread)
        if data["nextCursor"] is None or data["nextCursor"]["prev"] is None or found_old_threads:
            break
        prev_cursor = data["nextCursor"]["prev"]

# general channel
print("fetching general channel")
fetch_from_channel("1c19dd58-394e-412d-a853-f9075fbea34f")
print()

# support-question channel
print("fetching support-question channel")
fetch_from_channel("ae164b95-2204-44d4-9595-69c1cdaf17ad")
print()

# save threads as a json file
with open("processed/discord_threads.json", "w") as f:
    f.write(json.dumps(threads, indent=4))