import logging
import pyodbc
import os
import azure.functions as func
import json
import traceback
import requests
from datetime import datetime, timedelta

# Set up the Function app with anonymous auth level
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)
# Get environment variables
conn_str = os.getenv("SQL_CONNECTION_STRING")
slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")
# Set the threshold values for temperature and humidity
threshold_temperature = 8
threshold_humidity = 60.0


@app.route(route="fridge-reading", methods=["POST"])
def fridge_reading(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function to handle HTTP requests for recording fridge temperature and humidity readings.
    Args:
        req (func.HttpRequest): The HTTP request object containing JSON body with temperature, humidity, and fridge number.
    Returns:
        func.HttpResponse: The HTTP response object indicating the result of the operation.
            - 200: Data recorded successfully.
            - 400: Invalid temperature or humidity data.
            - 500: Database error.
    The function performs the following steps:
    1. Logs the trigger of the function.
    2. Parses the temperature, humidity, and fridge number from the JSON body of the request.
    3. Connects to the database and inserts the parsed data into the FridgeReadings table.
    4. Returns appropriate HTTP response based on the success or failure of the operation.
    """
    logging.info("FridgeReading function triggered.")

    # Parse temperature and humidity from JSON body
    try:
        req_body = req.get_json()
        temperature = float(req_body.get("temperature"))
        humidity = float(req_body.get("humidity"))
        fridgeNo = int(req_body.get("fridgeNo"))
    except (TypeError, ValueError, json.JSONDecodeError):
        return func.HttpResponse(
            "Invalid temperature or humidity data.", status_code=400
        )

    # Connect to the database and insert the data
    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO FridgeReadings (Temperature, Humidity, FridgeNo) VALUES (?, ?, ?)",
                (temperature, humidity, fridgeNo),
            )
            conn.commit()
    except Exception as e:
        logging.error(f"Database error: {e}")
        logging.error(f"Traceback: {traceback.format_exc()}")
        return func.HttpResponse("Database error.", status_code=500)

    return func.HttpResponse("Data recorded successfully.", status_code=200)


# Timer Trigger Function (runs every minute)
@app.function_name(name="check_recent_readings_timer")
@app.schedule(
    schedule="*/1 * * * *",
    arg_name="timer",
)
def check_recent_readings_timer(
    timer: func.TimerRequest,
) -> None:
    """
    This function is triggered by a timer and checks recent fridge readings from a database.
    It retrieves readings from the last minute and checks if any readings surpass predefined temperature or humidity thresholds.
    If any thresholds are breached, it sends an alert notification via Slack.
    Args:
        timer (func.TimerRequest): The timer request object that triggers this function.
    Raises:
        Exception: Logs any exceptions that occur during the execution of the function.
    """
    logging.info("CheckRecentReadings function triggered.")
    try:
        # Define the timestamp cutoff for last minute
        cutoff_time = datetime.now() - timedelta(minutes=1)

        # Connect to the database and retrieve recent entries
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT Temperature, Humidity, Timestamp, FridgeNo FROM FridgeReadings WHERE Timestamp >= ?",
                (cutoff_time,),
            )
            recent_readings = cursor.fetchall()

        # Check if any readings surpass the threshold
        alerts = []
        for reading in recent_readings:
            temperature, humidity, timestamp, fridgeno = reading
            if temperature > threshold_temperature or humidity > threshold_humidity:
                alerts.append(
                    f"Alert! Fridge with number {fridgeno} Temperature: {temperature}, Humidity: {humidity} at {timestamp}"
                )

        # If any alerts were triggered, send a Slack notification
        if alerts:
            alert_message = "\n".join(alerts)
            send_slack_notification(alert_message)
            logging.info("Slack notification sent due to threshold breach.")
        else:
            logging.info("No threshold breach detected.")

    except Exception as e:
        logging.error(f"Error in check_recent_readings: {e}")
        logging.error(f"Traceback: {traceback.format_exc()}")


def send_slack_notification(message: str):
    """
    Sends a notification to a Slack channel via Incoming Webhook.

    Args:
        message (str): The message to be sent to the Slack channel.

    Raises:
        Exception: If there is an error sending the notification.
    """
    try:
        payload = {"text": message}
        headers = {"Content-Type": "application/json"}
        response = requests.post(slack_webhook_url, json=payload, headers=headers)

        if response.status_code == 200:
            logging.info("Notification sent to Slack successfully.")
        else:
            logging.error(
                f"Failed to send Slack notification: {response.status_code}, {response.text}"
            )

    except Exception as e:
        logging.error(f"Error sending Slack notification: {e}")
