# fcm.py
# Created by abdularis on 24/10/17
#
# See firebase notification documentation for more details

import json
import requests


FCM_URL = 'https://fcm.googleapis.com/fcm/send'
MAX_REG_TOKENS = 1000

reg_id_errors = [
    'MissingRegistration',
    'InvalidRegistration',
    'NotRegistered'
]


def _send_request(server_key, fcm_message):
    """
    send request to firebase server

    :return: tuple (http response code, FcmResponseMessage or raw text if http resp != 200)
    """
    json_payload = str(fcm_message)

    headers = {
        'Authorization': 'key=%s' % server_key,
        'Content-Type': 'application/json'
    }

    print('sending fcm message...')
    resp = requests.post(FCM_URL, data=json_payload, headers=headers)
    if resp.status_code == 200:
        return resp.status_code, FcmResponseMessage(fcm_message, resp.json())
    return resp.status_code, resp.text


class FcmMessage:
    """
    Encapsulate firebase notification message
    """

    def __init__(self, registration_ids=None, to=None, condition=None, notification=None, data=None):
        if to:
            self.to = to
        else:
            self.registration_ids = registration_ids
        if condition:
            self.condition = condition

        if notification:
            if not isinstance(notification, dict):
                raise ValueError('"notification" must be type of dictionary.')
            self.notification = notification
        if data:
            if not isinstance(data, dict):
                raise ValueError('"data" must be type of dictionary.')
            self.data = data

    def __str__(self):
        """
        Dumps a json string from this class instance
        """
        return json.dumps(self.__dict__)


class FcmResponseMessage:
    """
    This class represents a firebase notification request response

    request: FcmMessage object (request)
    multicast_id:
    success:
    failure:
    canonical_ids:
    results: list of tuples of size two (registration_id, result dictionary from fcm results object)
    """

    def __init__(self, fcm_request_msg, json_msg_resp):
        self.request = fcm_request_msg
        self.multicast_id = json_msg_resp.get('multicast_id')
        self.success = json_msg_resp.get('success')
        self.failure = json_msg_resp.get('failure')
        self.canonical_ids = json_msg_resp.get('canonical_ids')

        self.results = []
        if hasattr(self.request, 'registration_ids') and json_msg_resp.get('results'):
            # it has sent to a list of registration ids
            self.results = [res for res in zip(self.request.registration_ids, json_msg_resp['results'])]
        elif hasattr(self.request, 'to') and json_msg_resp.get('results'):
            # it has sent to one registration only
            self.results = [(self.request.to, json_msg_resp['results'][0])]


class FcmNotification:
    """
    FcmNotification class is used to send a notification using firebase notification API
    """

    def __init__(self, server_key):
        """
        constructor

        :param server_key: Firebase server key
        """
        self.server_key = server_key

    def send(self, registration_ids, notification=None, data=None):
        """
        Send a firebase message to a list of users identified by registration ids

        :param registration_ids: list of token/registration id
        :param notification: notification dictionary data
        :param data: custom data to be send
        :return: list of tuple (http response code, FcmResponseMessage or raw text if http resp != 200)
        """
        responses = []
        curr_idx = 0
        while registration_ids[curr_idx:MAX_REG_TOKENS]:
            msg = FcmMessage(registration_ids=registration_ids[curr_idx:MAX_REG_TOKENS],
                             notification=notification,
                             data=data)
            resp = _send_request(self.server_key, msg)
            responses.append(resp)
            curr_idx += MAX_REG_TOKENS
        return responses

    def send_to(self, to, notification=None, data=None):
        """
        Send a firebase message to a specific user identified by registration id in 'to' parameter

        :param to: token/registration id (not topics)
        :param notification: notification dictionary data
        :param data: custom data to be send
        :return: tuple (http response code, FcmResponseMessage or raw text if http resp != 200)
        """
        msg = FcmMessage(to=to, notification=notification, data=data)
        return _send_request(self.server_key, msg)
