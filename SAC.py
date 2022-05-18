# All purpose application for all your SAC User Management. 
# Please see README file, on how to use and deploy the API. 
#

#Module imports:
from typing import Literal
import requests
import json
import base64

from requests.models import RequestEncodingMixin

#The config file contains all the program secrets. 
import config
#The file containing the bodies:
from BodyConstructor import BodyConstructor as Body

# Declare constants.
# Please see 'globalConfig' file, to add these values. 
sacBaseUrl = config.sacBaseUrl
oAuth2SAMLTokenUrl = config.oAuth2SAMLTokenUrl
clientId = config.clientId
clientSecret = config.clientSecret

class UrlConstructor:

    # Function for contructing request URLs.
    # Returns the base url,
    def fetchUrl(endpoint: Literal["bearer", "csrf", "users", "groups", "user", "group"], entity=""):
        '''Returns a url & endpoint. Note: User & Group requires the optional "entity" format'''
        if sacBaseUrl == "":
            raise ValueError("Base URL not defined")

        if endpoint.lower() == 'bearer':
            # The bearer URL is retrived from SAC -> Settings -> App. Integration -> Client.
            return str(oAuth2SAMLTokenUrl + 'grant_type=client_credentials')
        elif endpoint.lower() == 'csrf':
            return str(sacBaseUrl + '/api/v1/scim/Users')
        elif endpoint.lower() == 'users':
            return str(sacBaseUrl + '/api/v1/scim/Users')
        elif endpoint.lower() == 'groups':
            return str(sacBaseUrl + '/api/v1/scim/Groups')
        elif endpoint.lower() == 'user':
            return str(sacBaseUrl + '/api/v1/scim/Users' + '/' + entity)
        elif endpoint.lower() == 'group':
            return str(sacBaseUrl + '/api/v1/scim/Groups' + '/' + entity)
        else:
            raise ValueError("endpoint is undefined - please refer to the allowed list of endpoints.")


class HeaderConstructor:
    
    def getToken():
        '''Function for fetching the bearer token'''
        url = UrlConstructor.fetchUrl('bearer')

        Auth = '{0}:{1}'.format(clientId, clientSecret)
        headers = {'Authorization': 'Basic {0}'.format(base64.b64encode(Auth.encode('utf-8')).decode('utf-8'))}
        params = {'grant_type': 'client_credentials'}

        tokenRequest = requests.post(url, headers=headers, params=params)

        # HTTP ERROR Handling.
        if not str(tokenRequest.status_code) == '200':
            MessageHandler.httpRequestError(tokenRequest.status_code, "getToken", url, tokenRequest.json())
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

        #Important note: The CSRF-token recieved is unique to the session ID,
        #  and these two has to be passed at the same time. 
        return_payload = {}
        return_payload['Token'] = csrfRequest.headers['x-csrf-token']
        return_payload['Session'] = csrfRequest.headers['set-cookie']
        return return_payload

    def getHeaders(requestType="GET"):
        '''Returns the custom header, needed for the different requests. 
        POST & PUT requests also generates the required the csrf-token'''

        #Ini. dict
        headers = {}
        #Case handling. 
        requestType = requestType.upper()

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


class UserManagement:

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

        if returnType.lower() == "custom":
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

        if returnType.lower() == "json":
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

        userBody = Body.getRequestBody('create user')

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

        #Create User:
        postCreate = requests.post(
            url, headers=headers, data=json.dumps(userBody))

        #Add User to team. Because a user cannot be added 
        # to a team in the user creation step, we have 
        # to add the user to the team in an EditTeam operation .
        # Format Teams
        teamsBody = []

        # Format teams into correct SCHEMA.
        for team in teams:
            UserManagement.UpdateTeam(team, 'AddUser' ,members=[userName])


        return MessageHandler.httpCallReturn(postCreate)

    def createTeam(teamId, teamTxt, members=[], roles=[]):

        url = UrlConstructor.fetchUrl('groups')
        headers = HeaderConstructor.getHeaders('POST')

        teamBody = Body.getRequestBody('create team')

        memberBody = []
        # Format members into correct SCHEMA.
        for user in members:
            templateBody = Body.getRequestBody('add user')
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

    def addUserToTeam(userId, teamId):
        
        str(teamId).upper() if teamId == "" else ValueError("Please provide a valid Team ID")
        str(userId).upper() if userId == "" else ValueError("Please provide a valid user")

        UserManagement.UpdateTeam(teamId,'AddUser',members=userId)

        return


    def UpdateTeam(teamId, userOperation :Literal[ 'RemoveUsers', 'AddUser'], teamTxt="", members=[], roles=[], ):

        str(teamId).upper() if teamId == "" else ValueError("Please provide a valid Team ID")

        url = UrlConstructor.fetchUrl('group',teamId)
        headers = HeaderConstructor.getHeaders('POST')
        teamBody = Body.getRequestBody('create team')

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

        memberBody = []
        if members == "" or members == []:
            try:
                members = teamBody["members"]
                memberBody.append(members)
            except:
                members = ""
        else:
            if userOperation == 'RemoveUsers':
                memberBody = [user for user in teamBody["members"] if not user in members]
            elif userOperation == 'AddUser':
                for user in members:
                    templateBody = Body.getRequestBody('add user')
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
        userBody = Body.getRequestBody('create user')

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
            templateBody = Body.getRequestBody('add team')
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

    def httpCallReturn(request):
        ''' Function for formatting the http responses, to get better information from HTTP calls '''

        reponseBody = Body.getRequestBody('http return')

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
