# Helper classes for constructing URLS and getting tokens.
# Developed by InnoLogic A/S, Denmark.
# All code can be found at https://github.com/ChrisSorensen91/SAC_PUBLIC.git
# Have fun :)

from typing import Literal
import requests
import json
import base64

from requests.models import RequestEncodingMixin

# BEFORE YOU START:
# Please go into classes UrlConstructor and HeaderConstructor and maintain the values.
class MetaDataContainer:
    
    #TODO Test instanciation. 
    def __init__(self, sacBaseUrl, oAuth2SAMLTokenUrl, clientId, clientSecret):
        self.sacBaseUrl = sacBaseUrl
        self.oAuth2SAMLTokenUrl = oAuth2SAMLTokenUrl
        self.clientId = clientId
        self.clientSecret = clientSecret
        return self

    #TODO: Append classes to incorporate passing the metadata to functions.

    


class UrlConstructor:

    # Add the basic url for your SAC tenant:
    # You should be able to find the base url from you SAC landing page:
    # https://<THIS PART>/sap/fpa/ui/app.html#/home
    sacBaseUrl = ""

    def __init__(self):
        print("URL constructor instansiated")

    def __str__(self):
        print("Helper class: Fetching URLs and tokens")

    # Function for contructing request URLs.
    # Returns the base url,
    def fetchUrl(endpoint: Literal["bearer", "csrf", "users", "groups", "user", "group"], entity=""):
        '''Returns a url & endpoint. Note: User & Group requires the optional "entity" format'''
        if UrlConstructor.sacBaseUrl == "":
            raise ValueError("Base URL not defined")

        if endpoint == 'bearer':
            # The bearer URL is retrived from SAC -> Settings -> App. Integration -> Client.
            return str(HeaderConstructor.oAuth2SAMLTokenUrl + 'grant_type=client_credentials')
        elif endpoint == 'csrf':
            return str(UrlConstructor.sacBaseUrl + '/api/v1/scim/Users')
        elif endpoint == 'users':
            return str(UrlConstructor.sacBaseUrl + '/api/v1/scim/Users')
        elif endpoint == 'groups':
            return str(UrlConstructor.sacBaseUrl + '/api/v1/scim/Groups')
        elif endpoint == 'user':
            return str(UrlConstructor.sacBaseUrl + '/api/v1/scim/Users' + '/' + entity)
        elif endpoint == 'group':
            return str(UrlConstructor.sacBaseUrl + '/api/v1/scim/Groups' + '/' + entity)
        else:
            pass


class HeaderConstructor:

    # The bearer URL is retrived from SAC -> Settings -> App. Integration ->OAuth Clients.
    # Note: Some guides you find online might use the 'Token URL'. This procuded errors when i tried.
    oAuth2SAMLTokenUrl = ""

    # Both Client ID and secret are retrived from SAC -> Settings -> App. Integration -> Client.
    clientId = ""
    clientSecret = ""

    def __init__(self):
        print("Header constructor instansiated")

    def __str__(self):
        print("Helper class: Constructing header information")

    # Function for fetching the bearer token.
    # Client ID and secret are generated by your SAC tenant.
    # Follow the first step ("Configuration SAP Analytics Cloud") in this guide:
    # http://www.sapspot.com/how-to-use-rest-api-in-sap-analytics-cloud-to-update-user-profile-in-embedded-scenarios/,
    # to set up the provisioning agent.
    def getToken():
        '''Function for fetching the bearer token'''
        url = UrlConstructor.fetchUrl('bearer')

        # Thanks to Stefan Himmelhuber: Blog post:
        # https://blogs.sap.com/2020/02/06/sac-export-user-list-by-rest-api/
        # for a clever encoding method :)

        Auth = '{0}:{1}'.format(
            HeaderConstructor.clientId, HeaderConstructor.clientSecret)

        headers = {
            'Authorization': 'Basic {0}'.format(
                base64.b64encode(Auth.encode('utf-8')).decode('utf-8'))}

        params = {'grant_type': 'client_credentials'}

        tokenRequest = requests.post(url, headers=headers, params=params)

        # HTTP ERROR Handling.
        if not str(tokenRequest.status_code) == '200':
            MessageHandler.httpRequestError(
                tokenRequest.status_code, "getToken", url, tokenRequest.json())

        returnToken = tokenRequest.json()['access_token']

        return returnToken
    # Function for fetching the CSRF-token,

    def getCsrfToken():
        '''Returns the csrf token, for PUT and POST requests'''
        # Getting the CSRF token.
        url = UrlConstructor.fetchUrl('csrf')
        headers = HeaderConstructor.getHeaders()

        csrfRequest = requests.get(url, headers=headers)

        if not str(csrfRequest.status_code) == '200':
            MessageHandler.httpRequestError(
                csrfRequest.status_code, "getToken", url, csrfRequest.json())

        return_payload = {}
        return_payload['Token'] = csrfRequest.headers['x-csrf-token']
        return_payload['Session'] = csrfRequest.headers['set-cookie']
        return return_payload

    def getHeaders(requestType="GET"):
        '''Returns the custom header, needed for the different requests. 
        POST & PUT requests also generates the required the csrf-token'''

        #Ini. dict
        headers = {}

        # Required constants for the SAC API.
        headers['x-sap-sac-custom-auth'] = "true"
        # Custom section:
        headers['Authorization'] = 'Bearer ' + HeaderConstructor.getToken()

        # Additions for the different types of calls.
        # POST and PUT requires extra info; whereas GET only requires the Bearer.
        if requestType == "POST" or requestType == "PUT":
            csrfInfo = {}
            csrfInfo = HeaderConstructor.getCsrfToken()
            headers['Cookie'] = csrfInfo['Session']
            headers['x-csrf-token'] = csrfInfo['Token']
            headers['Content-Type'] = 'application/json'
        else:
            # Optional. dosen't hurt. Used in the GET call to fetch the token.
            headers['x-csrf-token'] = 'fetch'

        return headers


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


class UserManagement:

    def __init__(self) -> None:
        return "User management constructor instansiated"

    def __str__(self) -> str:
        return "Helper class: Manageing users and teams"

    def getGroups(returnType: Literal["json", "custom"], selectEntities=[], teams=[]):
        ''' Returns all groups, now called Teams, from SAC, eigther as raw json or select entities.
              Valid entities: "id", "displayName", "meta", "members", "roles"
              Specify a team ID in teams, for query a subset of teams. 
              '''

        urlList = []
        groupList = []

        # If list "Teams" was provided.
        if teams:
            for team in teams:
                url = UrlConstructor.fetchUrl('group', entity=team)
                urlList.append(url)
        else:
            url = UrlConstructor.fetchUrl('groups')
            urlList.append(url)

            # Get the request headers.
        headers = HeaderConstructor.getHeaders()

        if returnType == "custom":
            entityList = []
            MatchList = ["id", "displayname", "meta", "members", "roles"]
            # Collect the wanted entities and weed out the bad ones
            for entity in selectEntities:
                # Validate the entity is in the match list, otherwise pass.
                if not str(entity).lower() in MatchList:
                    continue  # <-- Discard
                entityList.append(entity)

            # Loop through the list of URLs.
            # For each url,
        for url in urlList:
            groupRequest = requests.get(url, headers=headers)

            if not str(groupRequest.status_code) == '200':
                MessageHandler.httpRequestError(
                    groupRequest.status_code, "getToken", url, groupRequest.json())

            if returnType == "json":
                groupList.append(groupRequest.json())

            if returnType == "custom":
                customPayload = {}
                groupRequestJson = groupRequest.json()

                # Collect the desired data into groupList
                for entity in entityList:
                    customPayload[entity] = groupRequestJson.get(entity)

                groupList.append(customPayload)

        return groupList

    def getUsers(returnType: Literal["json", "custom"], selectEntities=[], users=[]):
        ''' Returns all users from SAC, eigther as raw json or select entities.
            "userName", "id", "preferredLanguage", "meta", "name",  "members", "roles",
                "displayName", "active", "emails", "photos", "roles", "groups"
            '''

        urlList = []
        userList = []

        if users:
            for user in users:
                url = UrlConstructor.fetchUrl('user', entity=user)
                urlList.append(url)
        else:
            url = UrlConstructor.fetchUrl('users')
            urlList.append(url)

        if returnType == "custom":
            customPayload = {}
            entityList = []
            # Valid entities in the SAC user schema.
            MatchList = [
                "username", "id", "preferredLanguage",
                "meta", "name",  "members", "roles",
                "displayname", "active", "emails",
                "photos", "roles", "groups"]

        # Collect the wanted entities and weed out the bad ones
        for entity in selectEntities:
            # Validate the entity is in the match list, otherwise pass.
            if not str(entity).lower() in MatchList:
                continue  # <-- Discards the entity.

            entityList.append(entity)

        headers = HeaderConstructor.getHeaders()

        for url in urlList:
            userRequest = requests.get(url, headers=headers).json()

        if returnType == "json":
            return userRequest.json()

        if returnType == "custom":
            # Collect the desired data into groupList
            for user in userRequest["Resources"]:
                for entity in entityList:
                    customPayload[entity] = user.get(entity)

                userList.append(customPayload)

        return userList

    def assignPrivileges(userId, roles=[], teams=[]):

        if not roles and not teams:
            raise ValueError("No roles or teams provided")

        url = UrlConstructor.fetchUrl('user', userId)
        headers = HeaderConstructor.getHeaders("PUT")

        # Construct body:

        # Fetch the body of requests, in order to make changes.
        userBodyRequest = requests.get(url, headers=headers)
        if not str(userBodyRequest.status_code) == '200':
            MessageHandler.httpRequestError(
                userBodyRequest.status_code, "getToken", url, userBodyRequest.json())

        userBody = userBodyRequest.json()
        # Manipulate request body.
        userBody["roles"] = roles
        userBody["groups"] = teams

        putAssign = requests.put(url, headers=headers,
                                 data=json.dumps(userBody))
        if not str(putAssign.status_code) == '200':
            MessageHandler.httpRequestError(
                putAssign.status_code, "getToken", url, putAssign.json())

        return putAssign.json()
        

    def createUser(userName, familyName, emails,
                   firstName="", roles=[], teams=[], managerId=""):

        # NOTE: Users, not a single user.
        url = UrlConstructor.fetchUrl('users')
        headers = HeaderConstructor.getHeaders("POST")

        userBody = BodyConstructor.getRequestBody('create user')

        # Format Teams
        teamsBody = []

        # Format teams into correct SCHEMA.
        for team in teams:
            templateBody = BodyConstructor.getRequestBody('add team')
            templateBody["value"] = str(team).upper()
            templateBody["$ref"] = "/api/v1/scim/Groups/" + str(team).upper()

            teamsBody.append(templateBody)

        # Non required Body elements that can be manipulated:
        displayName = firstName + ' ' + familyName  # <-- Display name*

        # Assigning custom values to the
        userBody["userName"] = userName
        userBody["name"]["firstName"] = firstName
        userBody["name"]["familyName"] = familyName
        userBody["displayName"] = displayName
        userBody["emails"][0]["value"] = emails
        userBody["urn:scim:schemas:extension:enterprise:1.0"]["manager"]["managerId"] = managerId
        userBody["roles"] = roles
        userBody["groups"] = teamsBody

        postCreate = requests.post(
            url, headers=headers, data=json.dumps(userBody))

        return MessageHandler.httpCallReturn(postCreate)

    def createTeam(teamId, teamTxt, members=[], roles=[]):

        url = UrlConstructor.fetchUrl('groups')
        headers = HeaderConstructor.getHeaders('POST')

        teamBody = BodyConstructor.getRequestBody('create team')

        memberBody = []
        # Format members into correct SCHEMA.
        for user in members:
            templateBody = BodyConstructor.getRequestBody('add user')
            templateBody["value"] = str(user).upper()
            templateBody["$ref"] = "/api/v1/scim/Users/" + str(user).upper()

            memberBody.append(templateBody)

        teamBody["id"] = teamId
        teamBody["displayName"] = teamTxt
        teamBody["members"] = memberBody
        teamBody["roles"] = roles

        postCreate = requests.post(
            url, headers=headers, data=json.dumps(teamBody))

        return MessageHandler.httpCallReturn(postCreate)

    def UpdateTeam(teamId, teamTxt="", members=[], roles=[]):

        if teamId == "":
            str(teamId).upper()
        else:
            raise ValueError("Please provide a valid Team ID")

        url = UrlConstructor.fetchUrl('group',teamId)
        headers = HeaderConstructor.getHeaders('POST')
        teamBody = BodyConstructor.getRequestBody('create team')

        teamBodyResponse = requests.get(url, headers=headers)

        if not str(teamBodyResponse.status_code) == '200':
            MessageHandler.httpRequestError(teamBodyResponse.status_code, "getToken", url, teamBodyResponse.json())
        else:
            teamBody = teamBodyResponse.json()

        if teamTxt == "":
            try:
                teamTxt = teamBody["displayName"]
            except:
                teamTxt = ""
            
        if members == "" or members == []:
            try:
                members = teamBody["members"]
            except:
                members = ""
        else:
            memberBody = []
            for user in members:
                templateBody = BodyConstructor.getRequestBody('add user')
                templateBody["value"] = str(user).upper()
                templateBody["$ref"] = "/api/v1/scim/Users/" + str(user).upper()

                memberBody.append(templateBody)


        teamBody["id"] = teamId
        teamBody["displayName"] = teamTxt
        teamBody["members"] = memberBody
        teamBody["roles"] = roles
            
        putUpdate = requests.put(url, headers=headers, data=json.dumps(teamBody))

        return MessageHandler.httpCallReturn(putUpdate)

    def updateUser(userName, familyName="", emails="",
                   firstName="", roles=[], teams=[], managerId=""):

        url = UrlConstructor.fetchUrl('user', entity=userName)
        headers = HeaderConstructor.getHeaders("PUT")
        userBody = BodyConstructor.getRequestBody('create user')

        #Format input string. 
        if not userName == "":
            userName = str(userName).upper()
        else:
            raise ValueError("Enter a valid ID")

        # Format Teams
        teamsBody = []

        url = UrlConstructor.fetchUrl('user', userName)
        headers = HeaderConstructor.getHeaders("PUT")

        # Construct body:

        # Fetch the body of requests, in order to make changes.
        userBodyRequest = requests.get(url, headers=headers)
        if not str(userBodyRequest.status_code) == '200':
            MessageHandler.httpRequestError(userBodyRequest.status_code, "getToken", url, userBodyRequest.json())
        else:
            userBody = userBodyRequest.json()
        
        # Format teams into correct SCHEMA.
        for team in teams:
            templateBody = BodyConstructor.getRequestBody('add team')
            templateBody["value"] = str(team).upper()
            templateBody["$ref"] = "/api/v1/scim/Groups/" + str(team).upper()

            teamsBody.append(templateBody)

        #Preserve values from user body, if no input was given. 
        if firstName == "":
            try:
                firstName = userBody["name"]["firstName"]
            except:
                firstName = ""
        
        if familyName == "":
            try:
                familyName = userBody["name"]["familyName"] 
            except:
                familyName = ""
        
        if emails == "":
            try:
                emails = userBody["emails"][0]["value"]
            except:
                raise ValueError("Please provide a valid Email")
        
        if managerId == "":
            try:
                managerId = userBody["urn:scim:schemas:extension:enterprise:1.0"]["manager"]["managerId"]
            except:
                managerId = ""
        
        if roles == "":
            try:
                roles = userBody["roles"]
            except:
                roles = ""
       

        displayName = firstName + ' ' + familyName 
        userBody["userName"] = userName
        userBody["name"]["firstName"] = firstName
        userBody["name"]["familyName"] = familyName
        userBody["displayName"] = displayName
        userBody["emails"][0]["value"] = emails
        userBody["urn:scim:schemas:extension:enterprise:1.0"]["manager"]["managerId"] = managerId
        userBody["roles"] = roles
        userBody["Teams"] = teamsBody

        putUpdateUser = requests.put(
            url, headers=headers, data=json.dumps(userBody))

        return MessageHandler.httpCallReturn(putUpdateUser)
   

    def deleteUser(userId):
        ''' Deleting a user. NOTE: Contains NO confirmation or safeguard.
            PLEASE wrap this function, to avoid unintended deletions  '''

        url = UrlConstructor.fetchUrl('user', userId)
        headers = HeaderConstructor.getHeaders("POST")

        postDelete = requests.delete(url, headers=headers)

        return MessageHandler.httpCallReturn(postDelete)

    def deleteTeam(teamId):
        ''' Deleting a user. NOTE: Contains NO confirmation or safeguard.
            PLEASE wrap this function, to avoid unintended deletions  '''

        url = UrlConstructor.fetchUrl('group', teamId)
        headers = HeaderConstructor.getHeaders("POST")

        postDelete = requests.delete(url, headers=headers)

        return MessageHandler.httpCallReturn(postDelete)


class MessageHandler:

    def __init__(self):
        return "Message handler constructor instansiated"

    def __str__(self):
        return "Helper class: Return and error messages"

    def httpCallReturn(request):
        ''' Function for formatting the http responses, to get better information from HTTP calls '''

        reponseBody = BodyConstructor.getRequestBody('http return')

        try:
            reponseBody["status"] = request.status_code
        except:
            reponseBody["status"] = "Status not found"
        
        try:
            reponseBody["json"] = request.json()
        except:
            reponseBody["json"] = "no response body was returned"
        
        try:
            reponseBody["message"] = request.reason
        except:
            reponseBody["message"] = "No message returned"
        return reponseBody

    def httpRequestError(statusCode, callingFunction, url, response):

        statusMessage = "The call made by {} returned status code {} \n.".format(
            callingFunction, statusCode)

        recommendedAction = ""

        if str(statusCode) == '400':
            recommendedAction = '''Returncode 400 implies a 'Bad request'. The body of your request might contain illigal values.
               Please validate your request body against the schema, found at:
               https://api.sap.com/api/Story_API/schema.
               NOTE: If you were trying to assign a user to a team, please refer to SAP NOTE 2857395. \n
               Your request body were as follows: {}
            '''.format(response)
            raise ValueError(statusMessage + '\n' + recommendedAction)

        elif str(statusCode) == '403':
            recommendedAction = '''Returncode 403 implies a lack of authentication.
               Please validate that your have maintained client Id & secret in the UrlHandler class constructor. 
               NOTE: If you were trying to assign a user to a team or GET a team, please refer to SAP NOTE 2857395.
            '''
            raise ValueError(statusMessage + '\n' + recommendedAction)

        elif str(statusCode) == '404':
            recommendedAction = '''Returncode 404 implies the endpoint does not exist.
               Please validate the url {}. 
               NOTE: If you were trying to assign a user to a team or GET a team, please refer to SAP NOTE 2857395.
            '''.format(url)
            raise ValueError(statusMessage + '\n' + recommendedAction)

        elif str(statusCode) == '500':
            recommendedAction = '''Returncode 500 an error in the calling application.
               Please validate the log of your application. '''
            raise ValueError(statusMessage + '\n' + recommendedAction)
        pass
