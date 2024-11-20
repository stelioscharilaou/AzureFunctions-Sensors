# Deployment and Setup of Functions
1. Create an SQL database on Azure:
  
    Use the following Query to create the table:
    
    ```sql
    CREATE TABLE dbo.FridgeReadings (
        Id INT PRIMARY KEY NOT NULL,
        Temperature FLOAT NOT NULL,
        Humidity FLOAT NOT NULL,
        Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FridgeNo INT NOT NULL
    );

2. Get the ODBC SQL connection string for the database place and place it in the environmental variables file (.env) as SQL_CONNECTION_STRING
3. Create and deploy the functions included in the function_app.py
4. Get the default domain of the function application created and add the following to the end of the domain so the domain will invoke the fridge-reading function
    ```
    /api/fridge-reading
    ```
5. Add this domain in the .env file as AZURE_FUNCTION_URL
6. Create a channel in Slack and create a webhook for that channel. More information can be found [here](https://api.slack.com/messaging/webhooks) in Steps 1-3
7. Add the webhook URL in the .env file as SLACK_WEBHOOK_URL

# Use of Functions
1. Run the Python File run_sensors.py this should create random data to send to the functions for them to run
2. Note: Function check_recent_readings_timer always runs as it is on a timer
