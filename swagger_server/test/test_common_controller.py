# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.body import Body  # noqa: E501
from swagger_server.models.inline_response200 import InlineResponse200  # noqa: E501
from swagger_server.models.question_capsule import QuestionCapsule  # noqa: E501
from swagger_server.models.time_capsule import TimeCapsule  # noqa: E501
from swagger_server.test import BaseTestCase


class TestCommonController(BaseTestCase):
    """CommonController integration test stubs"""

    def test_info_get(self):
        """Test case for info_get

        Get user's info
        """
        response = self.client.open(
            '/VegetableP/Time-Capsule-Post-2019/1.0.0/info',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_question_capsule_cid_post(self):
        """Test case for question_capsule_cid_post

        Post new answer for question capsules
        """
        body = Body()
        response = self.client.open(
            '/VegetableP/Time-Capsule-Post-2019/1.0.0/question_capsule/{cid}'.format(cid=56),
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_question_capsules_get(self):
        """Test case for question_capsules_get

        Get question capsules
        """
        response = self.client.open(
            '/VegetableP/Time-Capsule-Post-2019/1.0.0/question_capsules',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_time_capsule_code_get(self):
        """Test case for time_capsule_code_get

        Get time capsule by code
        """
        response = self.client.open(
            '/VegetableP/Time-Capsule-Post-2019/1.0.0/time_capsule/{code}'.format(code='code_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_time_capsules_get(self):
        """Test case for time_capsules_get

        Get time capsules received by qrcode
        """
        response = self.client.open(
            '/VegetableP/Time-Capsule-Post-2019/1.0.0/time_capsules',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
