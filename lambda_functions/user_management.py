from datetime import datetime
from uuid import uuid4

import boto3
from boto3.dynamodb.conditions import Attr
from fastapi import FastAPI, HTTPException, Query, Response, status
from pydantic import BaseModel, EmailStr

API_VERSION = "v1"

# In production, you would use environment variables
# Initialize a DynamoDB client
dynamodb = boto3.resource('dynamodb')

# Reference your table
table = dynamodb.Table('users')


class User(BaseModel):
    full_name: str
    username: str
    email: EmailStr
    nationality: str

app = FastAPI(
    title="User Management API",
    description="User Management API documentation",
    version="1.0.0"
)

# Auxiliar function to check if the username or email already exists
def check_user_exists(username: str, email: str) -> bool:
    # Query to check for the username or email
    response = table.scan(
        FilterExpression=Attr('username').eq(username) | Attr('email').eq(email)
    )
    
    return 'Items' in response and len(response['Items']) > 0

#create user
@app.post(f"/{API_VERSION}/users", summary="Creates a new user", response_description="The created user data", responses={400: {"description": "Username or email already exists"}})
async def create_user(user: User):
    """
    Create a new user in the database.

    - **full_name**: Full name of the user.
    - **username**: Unique username for the user.
    - **email**: Email address of the user.
    - **nationality**: Nationality of the user.

    Returns the details of the created user including `userId`, `created_at`, and `modified_at` timestamps.
    """
    
    # Check if user already exists
    if check_user_exists(user.username, user.email):
        raise HTTPException(status_code=400, detail="Username or email already exists")
    
    # Generate UUID for the new user
    user_id = str(uuid4())
    
    # Prepare user data for insertion
    user_data = user.model_dump()  # Use .dict() to convert Pydantic model to dictionary
    user_data['userId'] = user_id  # Make sure this matches the primary key in your DynamoDB table
    user_data['created_at'] = datetime.now().isoformat()
    user_data['modified_at'] = user_data['created_at']
    
    # Insert the user into the table
    try:
        response = table.put_item(
            Item=user_data,
        )
    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
        raise HTTPException(status_code=500, detail="User already exists with this userId")
    
    # Check for successful insertion
    if response.get('ResponseMetadata', {}).get('HTTPStatusCode') == 200:
        return user_data
    else:
        raise HTTPException(status_code=500, detail="Internal Server Error")


#update
@app.patch(f"/{API_VERSION}/users/{{username}}", summary="Updates an existing user", response_description="Confirmation message")
async def update_user(username: str, user: User):
    """
    Update an existing user's details based on their username.

    - **username**: The username of the user to be updated.
    - **user**: The user data to update.

    Returns a confirmation message upon successful update.
    """
    
    # Retrieve the userId for the given username
    response = table.scan(
        FilterExpression=Attr('username').eq(username)
    )
        
    items = response.get('Items', [])

    if not items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")

    user_id = items[0]['userId']  # Assuming the first item is the correct one
    user_data = user.model_dump()
    user_data['modified_at'] = datetime.now().isoformat()

    # Update the user in DynamoDB using the userId
    try:
        response = table.update_item(
            Key={'userId': user_id},
            UpdateExpression="set full_name=:fn, email=:e, nationality=:nat, modified_at=:ma",
            ExpressionAttributeValues={
                ':fn': user_data['full_name'],
                ':e': user_data['email'],
                ':nat': user_data['nationality'],
                ':ma': user_data['modified_at']
            },
            ReturnValues="UPDATED_NEW"
        )
    except boto3.exceptions.Boto3Error as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    return {"message": "User updated successfully"}


@app.get(f"/{API_VERSION}/users/", summary="Lists all users", response_description="List of users")
async def list_users(filter: str = Query(None, description="Filter key and value separated by ':'"), fields: str = Query(None, description="Comma-separated list of fields to return")):
    """
    Retrieve a list of users with optional filtering and field selection.

    - **filter**: Filter the users based on a key-value pair.
    - **fields**: Specify which fields to include in the response for each user.

    Returns a list of users according to the specified filters and fields.
    """
    
    # Parse the filter
    filter_key, filter_value = None, None
    if filter:
        try:
            filter_key, filter_value = filter.split(":")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid filter format. Use 'key:value'.")

    # Perform the scan or query operation based on the filter
    if filter_key and filter_value:
        response = table.scan(FilterExpression=Attr(filter_key).eq(filter_value))
    else:
        response = table.scan()

    items = response.get('Items', [])

    if fields:
        # Split the fields string into a list of field names
        field_list = fields.split(',')
        # Filter each item to include only the specified fields
        filtered_items = [{field: item.get(field) for field in field_list if field in item} for item in items]
    else:
        # Return all fields if no specific fields are requested
        filtered_items = items

    return filtered_items

#delete
@app.delete(f"/{API_VERSION}/users/{{username}}", summary="Deletes a user by username", response_description="Confirmation message")
async def delete_user(username: str):
    """
    Delete a user based on their username.

    - **username**: The username of the user to be deleted.

    Returns a confirmation message upon successful deletion.
    """
    response = table.scan(
        FilterExpression=Attr('username').eq(username)
        )
    items = response.get('Items', [])  
    
    if not items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")
        # Check if the delete operation was successful
    
    try:
        user_id = items[0]['userId']
        response = table.delete_item(
                Key={'userId': user_id}
                )
        return {"message": "User deleted successfully"}
    except boto3.exceptions.Boto3Error as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


#deactivate
@app.patch(f"/{API_VERSION}/users/deactivate/{{username}}", summary="Deactivates a user", response_description="Confirmation message")
async def deactivate_user(username: str, user: User):
    """
    Deactivate a user account based on their username.

    - **username**: The username of the user to be deactivated.

    Returns a confirmation message upon successful deactivation.
    """
    
    # Query the user by username to get the userId
    response = table.scan(
        FilterExpression=Attr('username').eq(username)
    )
        
    items = response.get('Items', [])

    if not items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")

    user_id = items[0]['userId']  # Assuming the first item is the correct one
    user_data = user.model_dump()
    user_data['modified_at'] = datetime.now().isoformat()
    
    
    try:
        response = table.update_item(
            Key={'userId': user_id},
            UpdateExpression="set is_active = :ia",
            ExpressionAttributeValues={':ia': False},
            ReturnValues="UPDATED_NEW"
        )

        # Check if the update was successful
        if response.get('ResponseMetadata', {}).get('HTTPStatusCode') != 200:
            raise HTTPException(status_code=500, detail=f"Internal Server Error - {response}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": "User deactivated successfully"}


@app.options(f"/{API_VERSION}/ping", summary="Apis options", response_description="Confirmation message")
async def api_options():
    """
    Returns the allowed methods with status 204. Useful for test connection.
    """
    headers = {
        "Allow": "GET, POST, PATCH, DELETE, OPTIONS",
        "Content-Length": "0",
    }
    return Response(status_code=204, headers=headers)


#delete
@app.delete(f"/{API_VERSION}/delete/{{userId}}", summary="Deletes a user by userID", response_description="Confirmation message")
async def delete_user_john(userId):
    """
    Delete a user based on their userId.

    - **userId**: The userId of the user to be deleted.

    Returns a confirmation message upon successful deletion.
    """
    try:
        response = table.delete_item(
                Key={'userId': userId}
                )
        return {"response":response,"message": "User deleted successfully"}

    except boto3.exceptions.Boto3Error as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
