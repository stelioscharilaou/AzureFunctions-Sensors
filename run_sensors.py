import random
import os
import time
import requests
import threading

# URL of your Azure function endpoint
url = os.getenv("AZURE_FUNCTION_URL")
# Variables to track the start time and runtime limit
start_time = time.time()
runtime_limit = 60

def generate_random_data(fridge_no):
    """
    Generates random temperature and humidity data for a given fridge.

    Args:
        fridge_no (int): The identifier for the fridge.

    Returns:
        dict: A dictionary containing the temperature, humidity, and fridge number.
    """
    temperature = round(random.uniform(2, 8), 2)
    humidity = round(random.uniform(30, 55), 2)
    return {"temperature": temperature, "humidity": humidity, "fridgeNo": fridge_no}


def send_specific_data(data):
    """
    Sends specific data to a predefined URL using a POST request.
    Args:
        data (dict): The data to be sent in JSON format.
    Returns:
        None
    Raises:
        Exception: If there is an error while sending the data.
    """
    try:
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            print("Specific data sent successfully:", data)
        else:
            print(f"Failed to send specific data. Status code: {response.status_code}")
            
    except Exception as e:
        print(f"Error while sending specific data: {e}")


def send_data_to_azure(data):
    """
    Sends data to an Azure endpoint using a POST request.
    Args:
        data (dict): The data to be sent to the Azure endpoint in JSON format.
    Returns:
        None
    Raises:
        Exception: If there is an error while sending the data.
    """
    try:
        response = requests.post(url, json=data)

        if response.status_code == 200:
            print("Data sent successfully:", data)
        else:
            print(f"Failed to send data. Status code: {response.status_code}")

    except Exception as e:
        print(f"Error while sending data: {e}")


def sensor_simulation(fridge_no):
    """
    Simulates sensor data generation and sending for a specified fridge.

    Args:
        fridge_no (int): The identifier for the fridge being simulated.

    This function runs a loop that generates random data for the specified fridge,
    sends the data to Azure, and then sleeps for 10 seconds. The loop continues
    until the runtime limit is reached.
    """
    while time.time() - start_time < runtime_limit:
        data = generate_random_data(fridge_no)
        send_data_to_azure(data)
        time.sleep(10)


def specific_data_thread():
    """
    Continuously generates and sends specific data for a fridge within a runtime limit. (Wrong Data)
    Args:
        None
    Returns:
        None

    This function runs in a loop until the specified runtime limit is reached. In each iteration,
    it generates random temperature and humidity values within specified ranges, assigns them to
    a specific fridge number, and sends the data using the `send_specific_data` function. The loop
    pauses for 30 seconds between iterations.
    """
    while time.time() - start_time < runtime_limit:

        temperature = round(random.uniform(8, 12), 2)
        humidity = round(random.uniform(30, 55), 2)

        fridge_no = 4
        specific_data = {
            "temperature": temperature,
            "humidity": humidity,
            "fridgeNo": fridge_no,
        }

        send_specific_data(specific_data)

        time.sleep(30)


def main():
    """
    Main function to start sensor simulation and specific data threads.
    This function performs the following steps:
    1. Initializes an empty list to keep track of threads.
    2. Starts a thread for each fridge sensor simulation.
    3. Sleeps for 30 seconds to allow sensor threads to run.
    4. Starts a thread for sending specific data.
    5. Waits for all threads to complete before exiting.
    Note:
        The fridge sensor threads are started with fridge numbers beginning from 0.
    """
    threads = []

    # Start threads for each fridge
    for i in range(1):
        thread = threading.Thread(target=sensor_simulation, args=(i,))
        thread.start()
        threads.append(thread)

    time.sleep(30)
    
    # Start the thread for sending specific data
    specific_thread = threading.Thread(target=specific_data_thread)
    specific_thread.start()
    threads.append(specific_thread)

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main()
