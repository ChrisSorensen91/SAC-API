
## This file is intended as a demo-file, to show off the different functions in the InnoLogic SAC_API module 

## Import
import SAC

### Url metadata - Usually done in the background
## All three  needs to be filled out, as shown in the blog post: https://blogs.sap.com/2021/10/01/sac-user-management-with-the-rest-api-python/

clientID = SAC.HeaderConstructor.clientId
clientPW = SAC.HeaderConstructor.clientSecret
baseUrl = SAC.UrlConstructor.sacBaseUrl

### Fetch the various tokens. 

bearerToken = SAC.HeaderConstructor.getToken()
getHeaders = SAC.HeaderConstructor.getHeaders('GET') #<-- Returns the required headers for a GET request. 
postHeaders = SAC.HeaderConstructor.getHeaders('POST') #<-- Returns the required headers for a POST or PUT request. 

### Handling Users:
## Fetching USER info:
SAC.UserManagement.getUsers('json') #<-- Returns the raw information regarding all users in the SAC tenant.
SAC.UserManagement.getUsers('custom',selectEntities=["userName", "Id","emails"]) #<-- This is an example of a custom list, that returns the username, ID and email of all users. 
SAC.UserManagement.getUsers('custom',selectEntities=["displayName","groups"], users=["TEST123"]) #<-- This example will return the display name (usually full name) of user TEST123 and a list of all teams they are a part of. 

## Creating a user:
SAC.UserManagement.createUser("TEST456", "Testson", "<change>.com") # The most basic user creation: An ID, a sirname and an email. 
                                                                    # NOTE: SAC will automatically send a "Welcome" email, to the e-mail specified. 
SAC.UserManagement.createUser("TEST456", "Testson", "<change>.com", teams=["APITEAM"], managerId="BIGBOSS") #<-- A more elaborate version of user creation, that also assigns a manager and assigns the user to a team. 

## Updating a user:
SAC.UserManagement.updateUser("TEST456",familyName= "Sorensen") #<-- Updates the sirname of user TEST456. 

### Handling teams: 
## Fetching TEAM info:
SAC.UserManagement.getGroups('json') #<-- Returns the raw information regarding all the teams in the SAC Tenant. 
SAC.UserManagement.getGroups('custom',selectEntities=["displayName", "members"]) #<-- This is an example of a custom list, that return the description of all teams, and their members. 
SAC.UserManagement.getGroups('custom',selectEntities=["displayName", "members"], teams=["APITEAM"]) #<-- This is an example of a custom list, that return the description of all teams, and their members, but ONLY for the team APITEAM.

## Creating team:
SAC.UserManagement.createTeam("APITEAM", "My API Team", members=["TEST123", "TEST456"]) #<-- Example of creating a team. This will create the team APITEAM, with the description "My API Team" and two members. 

## Updateing Team: 
SAC.UserManagement.UpdateTeam("APITEAM","Text updated via API", members=["TEST123", "TEST456", "TEST789"]) # <-- This will take the team created in line 20, change the title and add an additional member. 
                                                                                                           #NOTE: The API does not feature a "PATCH" system. So you need to specify the full link of information, otherwise it will be overwritten.
                                                                                                           #NOTE: Adding a user to a team, after user creation, is done to the team, NOT the user. 