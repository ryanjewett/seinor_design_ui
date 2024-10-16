import requests
import os
import json

base_url = 'http://127.0.0.1:5000'

def loginCredValidation(username, password):
    data = {
        "username": username,
        "password": password
    }
    try:
        response = requests.post(f"{base_url}/login", json=data)
        #response.raise_for_status()  
    except requests.RequestException as e:
        print(f"Request failed: {str(e)}")
        return False
    
    if response.status_code == 200:
        return True
    else:
        print(f"Login failed with status code {response.status_code}: {response.text}")
        return False
    
def registerNewUser(username,password):
    data = {
        "username": username,
        "password": password
    }

    response = requests.post(f"{base_url}/reg", json=data)

    if response.status_code == 200:
        return True
    else:
        return False
    
def connectToServer():
    try:
        response = requests.get(f"{base_url}/")
        if response.text == "OK":
            return True
        else:
            return False
    except requests.RequestException as e:
        print(e)
        return False

def retriveDataChunk(date1,date2):

    tempfile = 'tempfile.json'

    if os.path.exists(tempfile):
        os.remove(tempfile)

    try:
        response = requests.get(f"{base_url}/getchk/real_data/{date1}/{date2}")
        response.raise_for_status()
        data = response.json()
        with open(tempfile, 'w') as f:
            json.dump(data,f, indent=4)
        return True
    except Exception as e:
        print("Error in retriving data chunk: "+ str(e))
        return False
