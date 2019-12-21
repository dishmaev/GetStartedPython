import requests

def test_available():

    url = " http://127.0.0.1:5000/"

    response = requests.request("GET", url)

    print(response.status_code)

    #print(response.text.encode('utf8'))
