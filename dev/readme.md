# [Deploying DynamoDB locally on your computer](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.DownloadingAndRunning.html)

## check connections

```bash
aws dynamodb list-tables --endpoint-url http://localhost:8000
```

Note: AWS credentials are saved in : "C:\Users\\[user]\.aws\config" and created in [IAM console](console.aws.amazon.com) in Access keys section.

## Create the table

```powershell
<sub>
# for bash don't forget to change ` with \ for line break
 aws dynamodb create-table `
>>     --table-name users `
>>     --attribute-definitions AttributeName=userId,AttributeType=S `
>>     --key-schema AttributeName=userId,KeyType=HASH `
>>     --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5
```

Output

```PowerShell
{   "TableDescription": {
        "AttributeDefinitions": [{"AttributeName": "userId",
                                  "AttributeType": "S"}],
        "TableName": "users",
        "KeySchema": [{"AttributeName": "userId",
                       "KeyType": "HASH"}],
        "TableStatus": "CREATING",
        "CreationDateTime": "2024-02-13T13:56:36.589000+00:00",
        "ProvisionedThroughput": {
            "NumberOfDecreasesToday": 0,
            "ReadCapacityUnits": 5,
            "WriteCapacityUnits": 5},
        "TableSizeBytes": 0,
        "ItemCount": 0,
        "TableArn": "arn:aws:dynamodb:eu-west-3:800962625409:table/users",
        "TableId": "f8509c1a-0dd5-4abc-9734-da712c0931f5",
        "DeletionProtectionEnabled": false}}
```
