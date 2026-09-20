# this will be used to develope the code to get Render to call the vehicle_reg function on my Ubuntu server
# will start with calling it from vscode on my Mac!
# the reg.py script was developed in another folder webappbasic/webapp2 and put on ubuntu but develope the
# code to execute it on a server here






# OLD **********************************************************************

# import requests

# def get_details(reg):
#     response = requests.get(
#         # "http://192.168.1.41:5000/run",       # local home network
#         "https://reg.moranai.net/run",         # over the net!
#         params={"reg": reg},
#         timeout=13
#     )

#     result = response.json()
#     return result




# if __name__ == '__main__':
#     # for testing:
#     print(get_details("232d1880"))


# OLD **********************************************************************


import requests


def get_details(reg):
    url = "https://www.vehicleservices.gov.ie/api/v1/public-cmv/cmv/vehicles/lookup"

    payload = {
        "registrationNumber": reg.upper()
    }

    response = requests.post(
        url,
        json=payload,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    vehicle = data.get("vehicleDetails", {})
    motor_tax = data.get("motorTaxDetails", {})
    nct = data.get("nctInformation", {})

    return {
        "Registration": vehicle.get("vehicleRegistrationNumber"),
        "Make": vehicle.get("vehicleMake"),
        "Model": vehicle.get("vehicleModel"),
        "Colour": vehicle.get("vehicleColourEn"),
        "Current Annual Motor Tax Rate": motor_tax.get("annualMotorRate"),
        "Motor Tax Expiry": motor_tax.get("motorTaxExpiryDate"),
        "NCT Expiry": nct.get("nctExpiryDate"),
        "Motor Tax Status": motor_tax.get("statusEn"),
        "NCT Status": nct.get("nctStatusEn")
    }


if __name__ == "__main__":
    print(get_details("191D11886"))
