# this will be used to develope the code to get Render to call the vehicle_reg function on my Ubuntu server
# will start with calling it from vscode on my Mac!
# the reg.py script was developed in another folder webappbasic/webapp2 and put on ubuntu but develope the
# code to execute it on a server here

import requests

def get_details(reg):
    response = requests.get(
        # "http://192.168.1.41:5000/run",       # local home network
        "https://reg.moranai.net/run",         # over the net!
        params={"reg": reg},
        timeout=13
    )

    result = response.json()
    return result




if __name__ == '__main__':
    # for testing:
    print(get_details("232d1880"))


