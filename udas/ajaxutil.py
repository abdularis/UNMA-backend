# ajaxutil.py
# Created by abdularis on 18/10/17

from flask import jsonify, make_response

STAT_SUCCESS = 'success'
STAT_INVALID = 'invalid'
STAT_ERROR = 'error'


def create_response(status, html_form=None, html_list=None, html_error=None, html_extra=None, scode=200):
    """
    Create response for ajax request

    :param status: either STAT_SUCCESS request was successfully done,
                    STAT_INVALID if the user input form data was not valid,
                    STAT_ERROR denote that there was an error while the task was performed
    :param html_form: html form to be included in a response
    :param html_list: list of data (doesn't have to be a <ul>, <ol> etc.)
    :param html_error:
    :param html_extra:
    :param scode: http status/response code
    :return: flask response object
    """
    json = jsonify(
            status=status,
            html_form=html_form,
            html_list=html_list,
            html_error=html_error,
            html_extra=html_extra)
    return make_response(json, scode)
