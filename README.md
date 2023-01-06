# Async Chat Client
 

A UI to interact with Minecraft chat
![Example](/example_pictures/example.png?raw=true "Example")

## Install Requirements

```sh
pip3 requirements.txt
```

## Reading and writing in the chat

```sh
python3 main.py
```

## Configuration options

| Key        | Description                | Required |
| ---------- | -------------------------- | -------- |
| host       | Host of chat to connect to | False    |
| port       | Port of chat to connect to | False    |
| history    | File to save chat history  | False    |
| token      | Chat access token          | False    |
| creds_file | Path to file with token    | False    |


## Register to be able to write in the chat

```sh
python3 register.py
```

## Configuration options

| Key        | Description                | Required |
| ---------- | -------------------------- | -------- |
| host       | Host of chat to connect to | False    |
| port       | Port of chat to connect to | False    |
| creds_file | Path to file with token    | False    |

![Example](/example_pictures/reg_example.png?raw=true "Example")