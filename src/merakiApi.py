"""
Defining the functionality of different Meraki API used for application functionality
"""
from flask import g
import requests
from PIL import Image
from io import BytesIO

# Base Meraki API Url
BASE_URL = "https://api.meraki.com/api/v1"


# ---------- MERAKI API FUNCTION DEFINITIONSS ----------
def getOrgs():
    """
    GET Organizations API
    :return:
    """
    url = "{}/organizations".format(BASE_URL)
    headers = {'X-Cisco-Meraki-API-Key': g.user['accessToken']}
    response = requests.request("GET", url, headers=headers)

    # print('REQUEST: GET Organizations')
    # print('RESPONSE: {}'.format(response.json()))

    return response.json()


def getOrg(orgId):
    """
    GET Organizations API
    :param orgId:
    :return:
    """
    url = "{}/organizations/{}".format(BASE_URL, orgId)
    headers = {'X-Cisco-Meraki-API-Key': g.user['accessToken']}
    response = requests.request("GET", url, headers=headers)

    # print('REQUEST: GET Organization')
    # print('RESPONSE: {}'.format(response.json()))

    return response.json()


def getNetworks(orgId):
    """
        GET Organizations API
        :param orgId:
        :return:
        """
    url = "{}/organizations/{}/networks".format(BASE_URL, orgId)
    headers = {'X-Cisco-Meraki-API-Key': g.user['accessToken']}
    response = requests.request("GET", url, headers=headers)

    # print('REQUEST: GET Networks')
    # print('RESPONSE: {}'.format(response.json()))

    return response.json()


def getNetworkDevices(networkID):
    """
        GET Organizations API
        :param networkID:
        :return:
        """
    url = "{}/networks/{}/devices".format(BASE_URL, networkID)
    headers = {'X-Cisco-Meraki-API-Key': g.user['accessToken']}
    response = requests.request("GET", url, headers=headers)

    # print('REQUEST: GET Network Devices')
    # print('RESPONSE: {}'.format(response.json()))

    return response.json()


def getLiveCameraState(serial_number):
    """
    Gets Meraki MV camera Snapshot at a given time
    :param serial_number:
    :return:
    """
    # Get video link
    url = "{}/devices/{}/camera/analytics/live".format(BASE_URL, serial_number)
    headers = {'X-Cisco-Meraki-API-Key': g.user['accessToken']}

    response = requests.request("POST", url, headers=headers)

    # print('REQUEST: GET Camera Snapshot')
    # print('RESPONSE: {}'.format(response.json()))

    return response.json()


def getCameraScreenshot(serial_number, timestamp):
    """
    Gets Meraki MV camera Snapshot at a given time
    :param serial_number:
    :param timestamp:
    :return:
    """
    # Get video link
    url = "{}/devices/{}/camera/generateSnapshot".format(BASE_URL, serial_number,timestamp)
    headers = { 'X-Cisco-Meraki-API-Key': g.user['accessToken'] }

    if timestamp is None:
        response = requests.request("POST", url, headers=headers)
    else:
        body = {"timestamp": timestamp}
        response = requests.request("POST", url, headers=headers, data=body)

    # print('REQUEST: GET Camera Snapshot')
    # print('RESPONSE: {}'.format(response.json()))

    return response.json()


def saveImage(url):
    try:
        # print('Retrieving image at: {}'.format(url))
        response = requests.get(url)
        image = Image.open(BytesIO(response.content))
        fileName = ''
        return image
    except Image.UnidentifiedImageError:
        saveImage(url)
