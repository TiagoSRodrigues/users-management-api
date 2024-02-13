# Project to create a User management microservice architecture

## Requirements

Create microservice for user management. This service performs all CRUD actions related to users, as follows:

- **Create User**: Accepts user information (name, username, email, nationality) and adds a new user to the database.
- **Read User**: Retrieves user information based on user ID.
- **Update User**: Accepts updated user information and modifies the corresponding user's data in the database. This could include updating profile details.
- **Delete User**: Removes a user from the database based on the provided user ID.

## Project structure

```bash
.
├── dev
│   ├── dynamodb
│   │   └── shared-local-instance.db
│   ├── dynamodb-docker-compose.yml
│   └── readme.md
├── lambda_functions
│   ├── __init__.py
│   ├── test_user_management.py
│   └── user_management.py
├── readme.md
```
