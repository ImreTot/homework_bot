# Homework bot
_Telegram bot checks the status of homework on the Yandex.Practice service._

## Installation and operation
The bot module is completely ready for use. It written on Python3.9 version. After running virtual enviroment run this command to install dependencies:
```sh
pip install requirements.txt
```
After launching, an eternal loop runs in the body of the code, which sends a request to the server at a certain frequency. By default, the module defines a constant for a pause of 600 seconds (`RETRY_PERIOD`).  

For the module to work, a `.env` file with environment variables is required. Here is their list: 
- PRACTICUM_TOKEN – token of the user whose account should be verified
- TELEGRAM_TOKEN – bot token
- TELEGRAM_CHAT_ID – chat token where messages should be sent  
The module handles errors of missing environment variables, bad network connection, and API errors to which requests are sent. Logging is also configured.

## License
MIT  
**Free Software, Hell Yeah!**
