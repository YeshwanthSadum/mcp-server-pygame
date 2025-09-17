# POST http://127.0.0.1:8000/move_left

import requests
response = requests.post("http://127.0.0.1:8000/jump")
print(response.json())