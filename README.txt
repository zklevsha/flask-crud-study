Basic CRUD REST API service with authentication/authization logic

REQUIREMENTS
docker + docker-compose

HOW TO RUN
sudo docker-compose up
This command will start application and postgress containers
After starting, enpoins will be available at :80 port

ENDPOINS
GET /users
lists all users

GET /users/<id>
Get single user by ID

POST /users/
Adding new user (full permisson required)
BODY: {"name": "<name>","password": "<password>", "permission_id": <id>}

PUT /users/<userid>
Updating user attributes (full permision required)
BODY: {"name": "<name>"," password": "<password>", "permission_id": <id>}
Omit attribures that you don`t want to update

GET /permissions
Get all available permissions


AUTHENTICATION
Service uses Basic Auth as login mechanism.
There are two test users
- username: user, password: user (read-only permission)
- username: admin, password: admin (full access permition)