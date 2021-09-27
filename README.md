# SAC-API

Welcome to the comprehensive SAC api, developed by Innologic, Denmark.

In this folder, you'll find a fully fletched Python 3.9 module, capable of handling all your SAC API user management needs.

The rep. consists of two main components:
* The SAC.py file, which is all the working code.
* A very lightweight, very ugly, Flask application, for testing / demo purposes.

</b>The SAC.py file:</b>

This file consists of five classes:
- UrlConstructor: Which is the base component for generating the correct URLs for your REST calls.
- HeaderConstructor: Which handles the construction of a request header, with all the relevant information needed for GET, PUT, POST and DELETE requests.
- BodyConstructor: which returns the required request body for POST requests.
- UserManagement: Which handles the GET, PUT and POST requests to your SAC tenant.
- ErrorHandling: Which is essentially a message class, that tries to return a usable error message to the user, and provide 'helpful' feedback.

The two first classes have static attributes, which you are required to fill out.

For a full rundown of how the code works, please refer to my SAP Blog post:

