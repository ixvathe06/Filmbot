import requests

def upload(img_path, client_id="6bfeea047ce4f80"):
    url = "https://api.imgur.com/3/image"
    headers = {"Authorization": f"Client-ID {client_id}"}
    with open(img_path, "rb") as img_file:
        data = {"image": img_file.read()}
        response = requests.post(url, headers=headers, files=data)
    if response.status_code == 200:
        return response.json()["data"]["link"]
    else:
        return f"Xatolik: {response.status_code}, {response.json()}"

