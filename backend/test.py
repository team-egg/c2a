import requests
from sseclient import SSEClient
import json

# curl -X POST -H "Content-Type: application/json" -d '{"message_id":"ca23c4d6-09bf-4ce3-8c63-87a60a8b8df2", "history":[{"role": "user", "label": "Login", "address": "0xdd20cC951372F4a82E9Ba429F805084180C20643"}, {"role": "user", "message": "TEST TX"}]}' https://c2a.puppy9.com/api/message
baseurl = "https://c2a.puppy9.com/api/message"

data_test_tx = {
    "message_id": "ca23c4d6-09bf-4ce3-8c63-87a60a8b8df2",
    "history": [
        {
            "role": "user",
            "label": "Login",
            "address": "0xdd20cC951372F4a82E9Ba429F805084180C20643"
        },
        {
            "role": "user",
            "message": "TEST TX"
        }
    ]
}

data_test_c2a = {
    "message_id": "ca23c4d6-09bf-4ce3-8c63-87a60a8b8df2",
    "history": [
        {
            "role": "bot",
        },
        {
            "role": "user",
            "message": "Help me check 0x19B57F2Ee33bcFDE75c1496B3752D099fc408Ef1 on Base Sepolia.",
            "label": "Contract-to-Action",
        }
    ]
}

def test_with_data(data):
    response = requests.post(baseurl, json=data, stream=True)
    client = SSEClient(response)

    mode = "md"
    for event in client.events():
        if event.data == "@@@":
            mode = "json"
            continue
        if event.data == "[DONE]":
            break
        if mode == "md":
            print(json.loads(event.data), end="", flush=True)
            # print(f"Received event: {event.event}, Data: {event.data}")
        else:
            print()
            print(json.dumps(json.loads(event.data), indent=4))


if __name__ == "__main__":
    test_with_data(data_test_c2a)
