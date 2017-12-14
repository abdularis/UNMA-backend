# fcm.py
# Created by abdularis on 24/10/17

import json
import requests


FCM_URL = 'https://fcm.googleapis.com/fcm/send'
MAX_REG_TOKENS = 1000

android_notif_key = [
    'title',
    'body',
    'android_channel_id',
    'icon',
    'sound',
    'tag',
    'color',
    'click_action',
    'body_loc_key',
    'body_loc_args',
    'title_loc_key',
    'title_loc_args'
]

reg_id_errors = [
    'MissingRegistration',
    'InvalidRegistration',
    'NotRegistered'
]


def _send_request(server_key, fcm_message):
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
        return json.dumps(self.__dict__)


class FcmResponseMessage:

    def __init__(self, fcm_request_msg, json_msg_resp):
        self.request = fcm_request_msg
        self.multicast_id = json_msg_resp.get('multicast_id')
        self.success = json_msg_resp.get('success')
        self.failure = json_msg_resp.get('failure')
        self.canonical_ids = json_msg_resp.get('canonical_ids')

        self.results = []
        if hasattr(self.request, 'registration_ids') and json_msg_resp.get('results'):
            self.results = [res for res in zip(self.request.registration_ids, json_msg_resp['results'])]
        elif hasattr(self.request, 'to') and json_msg_resp.get('results'):
            self.results = [(self.request.to, json_msg_resp['results'][0])]


class FcmNotification:

    def __init__(self, server_key):
        self.server_key = server_key

    def send(self, registration_ids, notification=None, data=None):
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
        :param notification:
        :param data:
        :return: FcmResponseMessage object
        """
        msg = FcmMessage(to=to, notification=notification, data=data)
        return _send_request(self.server_key, msg)
