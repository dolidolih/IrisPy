# IrisPy - Python Interface for Iris (KakaoTalk Bot)

IrisPy is a Python-based application designed to interact with **Iris**, the Android native KakaoTalk bot. It acts as a bridge, receiving real-time message events from Iris running on an Android device and allowing you to define your bot's responses and logic in Python.

**Key Features:**

*   **Receives Real-time KakaoTalk Messages:**  IrisPy sets up an HTTP endpoint (`/db`) to receive POST requests from Iris whenever a new message is detected in KakaoTalk.
*   **Processes Messages with Python Logic:**  You can define custom Python functions (within `chatbot/Response.py`) to process incoming messages, trigger actions, and generate responses.
*   **Sends Replies to KakaoTalk:** Using the `Replier` class, IrisPy can send text and image messages back to KakaoTalk through Iris's HTTP API.
*   **KakaoTalk Database Querying:**  The `KakaoDB` class provides methods to query the KakaoTalk database via Iris's `/query` endpoint, allowing you to retrieve information programmatically.

## Getting Started

### Installation

1.  **Clone the IrisPy repository** (if you are distributing the code, otherwise just copy the files):
    ```bash
    cd ~
    git clone https://github.com/dolidolih/IrisPy.git
    cd IrisPy
    ```

2.  **Run Setup Script:**
    This script only supports Ubuntu. If you are using different OS, see redroid docs.
    If you have installed pykakaodbbot earlier, skip this phase.
    ```bash
    chmod +x setup1.sh
    ./setup1.sh
    ```

3.  **Install Python Virtual Environment and Dependencies:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

4.  **Configure `config.json`:**
    Create a `config.json` file in the IrisPy directory with the following structure:

    ```json
    {
      "bot_endpoint": "http://[YOUR_ANDROID_DEVICE_IP]:[IRIS_BOT_HTTP_PORT]",
      "bot_id": [YOUR_KAKAO_TALK_USER_ID],
      "bot_name": "[YOUR_BOT_NAME]"
    }
    ```

    *   `bot_endpoint`: The base URL of your Iris HTTP server running on your Android device. Replace `[YOUR_ANDROID_DEVICE_IP]` with the IP address of your Android device and `[IRIS_BOT_HTTP_PORT]` with the port you configured in Iris's `config.json` (e.g., `"http://192.168.1.100:8080"`).
    *   `bot_id`: Your KakaoTalk BOT's user ID. You can find this when you run Iris.
    *   `bot_name`: Your bot's name, for internal identification within IrisPy.

### Running IrisPy

You can run IrisPy in two main ways, each suitable for different scenarios:

#### 1. Running in the Foreground (Development/Testing) - `python app.py`

    This method is ideal for development, testing, and debugging.

    *   **Command:**
        ```bash
        python app.py
        ```

    *   **Behavior:**

        *   Starts the Flask development server directly in your terminal.
        *   Logs and outputs are displayed in the terminal.
        *   **Stops when you close the terminal or interrupt the process (Ctrl+C).**
        *   Good for quickly testing changes and observing output in real-time.

#### 2. Running as a System Service (Background/Production) - `sudo systemctl restart chatbot`

    This method is recommended for deploying IrisPy as a reliable background service, suitable for a 24/7 chatbot.

    *   **Setup:** You need to have set up IrisPy as a system service using a service unit file (like `chatbot.service` provided in the `setup1.sh` example).  This typically involves copying the service file to `/etc/systemd/system/` and enabling it. (Refer to the `setup1.sh` script for an example service file).

    *   **Restart Command (after initial setup):**
        ```bash
        sudo systemctl restart chatbot
        ```

    *   **Other `systemctl` Commands:**

        *   `sudo systemctl start chatbot`: Starts the service.
        *   `sudo systemctl stop chatbot`: Stops the service.
        *   `sudo systemctl status chatbot`: Checks the service status and logs.
        *   `sudo systemctl enable chatbot`: Enables the service to start on boot.
        *   `sudo systemctl disable chatbot`: Disables the service from starting on boot.

    *   **Behavior:**

        *   Runs IrisPy in the background as a system service managed by `systemd`.
        *   **Automatically restarts if the application crashes or exits unexpectedly**, ensuring higher uptime.
        *   Logs are typically directed to system logs (e.g., accessible via `journalctl -u chatbot`).
        *   Runs persistently even after you close your terminal or reboot the server (if enabled).
        *   Ideal for production environments where you need the bot to be continuously available.

**Key Difference:**

The crucial distinction is **process management and persistence**. `python app.py` is a simple foreground process, while `systemctl restart chatbot` manages IrisPy as a robust, background service with automatic restarting and system-level logging. Choose `systemctl` for reliable, always-on bot operation and `python app.py` for development and quick testing.

## Usage

1.  **Start IrisPy:** Run IrisPy using either `python app.py` or `sudo systemctl restart chatbot` as described above.

2.  **Configure Iris (Android) to send events:** Ensure Iris on your Android device is configured to send HTTP POST requests to the IP address and port where IrisPy is running, specifically to the `/db` endpoint.  This is usually set up in Iris's configuration.

3.  **Customize Bot Logic in `chatbot/Response.py`:**  Edit the `chatbot/Response.py` file to define how your bot should respond to KakaoTalk messages.

    *   **Example (`chatbot/Response.py`):**

        ```python
        def response(room, msg, sender, replier, msg_json, db, g):
            if msg == "!hi":
                replier.reply("Hello from IrisPy!")
            # ... add more logic and commands ...
        ```

    *   The `response` function is the core logic handler. It receives:

        *   `room`: The chat room name.
        *   `msg`: The decrypted message content.
        *   `sender`: The sender's name.
        *   `replier`: An instance of the `Replier` class to send replies.
        *   `msg_json`: The raw JSON data received from Iris (the `json` field in the POST request).
        *   `db`: An instance of the `KakaoDB` class for database interaction.
        *   `g`: A shared dictionary (for inter-process communication, if needed).

4.  **Interact with your bot in KakaoTalk:** Send messages to your KakaoTalk account from another account. If your message matches the conditions in your `chatbot/Response.py` logic (e.g., starts with `!hi`), IrisPy will process it and send a reply back to KakaoTalk via Iris.

## Disclaimer

This project is provided for educational and research purposes only. Use it responsibly and ethically, respecting KakaoTalk's terms of service and user privacy. The developers are not responsible for any misuse or damage caused by this software.