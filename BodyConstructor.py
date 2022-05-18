#Module for body constructions and the different 
from typing import Literal

class BodyConstructor:

    def __init__(self) -> None:
        print("Body constructor instansiated")

    def __str__(self) -> str:
        print("Helper class: Constructing request body information")

    def getRequestBody(requestType: Literal['http return', 'create user', 'create team', 'add user', 'add team'], includeOptional=False):
        '''Returns the request body for creating eigther a team or a user.
           The parameter "includeOptional" will append a host of optional fields to the scehma, if needed.
           Optional parameters include, but are not limited to: Preferred language, date formatting ect. 
        '''
        # NOTE: The reason we 'hardcode' the schema for user creation, rather than
        # getting it via a GET call, is because existning users contain more information
        # then is allowed in the post call. Reusing the schema will result in a 400 error.
        # Schema was copied from: https://help.sap.com/viewer/298f82da4b184d1fb825b7ffe365e94a/release/en-US/da3dc52a0fd44da4b727c89d26326af6.html

        # The parameter to "Include optinal" will, if true, append the schema with addiotional fields.

        requestBody = {}

        if requestType.lower() == "http return":
            requestBody = {
                "status": "<HTTP STATUS CODE>",
                "raw": "<JSON>",
                "message": "<HTTP RESPONSE>"
            }

            return requestBody

        elif requestType.lower() == "create user":
            requestBody = {
                "schemas": ["ietf:params:scim:schemas:core:2.0:User",
                            "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User"],
                "userName": "<REQ ID>",
                "name":
                {
                    "firstName": "<FIRST NAME>",
                    "familyName": "<LAST NAME>"
                },
                "displayName": "<DISPLAY NAME>",
                "emails": [
                    {
                        "value": "<WORK EMAIL>",
                        "type": "work",
                        "primary": "true"
                    }
                ],
                "roles": [],
                "groups": [],
                "urn:scim:schemas:extension:enterprise:1.0": {
                    "manager": {
                        "managerId": "<MANAGER ID>"
                    }
                }
            }

            if includeOptional:

                optionalParameters = {
                    "urn:ietf:params:scim:schemas:extension:sap:user-custom-parameters:1.0": {
                        "dataAccessLanguage": "en",
                        "dateFormatting": "MMM d, yyyy",
                        "timeFormatting": "H:mm:ss",
                        "numberFormatting": "1,234.56",
                        "cleanUpNotificationsNumberOfDays": 0,
                        "systemNotificationsEmailOptIn": "true",
                        "marketingEmailOptIn": "false",
                        "isConcurrent": "true"
                    }
                }

                requestBody.update(optionalParameters)

        if requestType.lower() == "create team":
            requestBody = {
                "id": "<TEAM ID>",
                "displayName": "<TEAM DESC>",
                "members": [
                    {
                        "type": "User",
                        "value": " <USER ID> ",
                        "$ref": "/api/v1/scim/Users/<USER ID> "
                    }
                ],
                "roles": []
            }

            if includeOptional:
                optionalParameters = {
                    "urn:ietf:params:scim:schemas:extension:sap:group-custom-parameters:1.0": {
                        "admins": [
                            "User1"
                        ],
                        "moderators": [
                            "User1",
                            "User2"
                        ]
                    }
                }
                requestBody.update(optionalParameters)
        if requestType.lower() == "add user":
            requestBody = {
                "type": "User",
                "value": " <USER ID> ",
                "$ref": "/api/v1/scim/Users/<USER ID>"
            }

        if requestType.lower() == "add team":
            requestBody = {
                "value": "<TEAM ID>",
                "display": "<TEAM TEXT>",
                "$ref": "/api/v1/scim/Groups/<TEAM ID>"
            }
        if requestType.lower() == 'add email':
            requestBody = {
                "value": "<EMAIL>",
                "type": "<TYPE>",
                "primary": "<VALUE>"
            }

        return requestBody
