# EC-Team-16-distributed-file-orchestration-and-synchronization

This project implements a client-server application to manage file operations such as upload, download, preview, delete, and directory listing. The system supports multiple clients and ensures secure access to user directories.

---

## Table of Contents
1. [Introduction](#introduction)
2. [Features](#features)
3. [Architecture](#architecture)
4. [System Requirements](#system-requirements)
5. [Installation](#installation)
6. [Usage](#usage)
7. [File Descriptions](#file-descriptions)
8. [Logging](#logging)
9. [Error Handling](#error-handling)
10. [Future Enhancements](#future-enhancements)

---

## Introduction
The file management system allows clients to connect to a server, authenticate themselves, and perform file operations in their dedicated directories. The server supports a limited number of concurrent clients and employs a timeout mechanism to handle inactive connections.

---

## Features
- **User Authentication**: Each user has a unique username and password stored in a credentials file (`id_passwd.txt`).
- **File Operations**:
  - Upload
  - Download
  - Preview (first 1024 bytes)
  - Delete
  - Directory listing
- **Timeout**: Clients inactive for a specified duration (`100` seconds) are automatically disconnected.
- **Concurrency**: The server handles multiple clients concurrently using semaphores and thread pool.
- **Logging**: Both client and server activities are logged for monitoring and debugging purposes.

---

## Architecture
1. **Client**:
   - Sends requests to the server after authentication.
   - Displays server responses and performs user-requested operations.
2. **Server**:
   - Authenticates users and manages individual directories.
   - Executes file operations requested by clients.
   - Handles concurrency and ensures secure file access.

---

## System Requirements
- **Python Version**: Python 3.7 or above.
- **Libraries**:
  - `socket`
  - `os`
  - `signal`
  - `sys`
  - `time`
  - `concurrent.futures`
  - `maskpass`
  - Custom modules: `file_upload`, `file_download`, `file_preview`, `file_delete`, `logger_util`

---

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/file-management-system.git
   cd file-management-system
   ```
2. Install dependencies:
   ```bash
   pip install maskpass
   ```
3. Create the directory structure:
   ```bash
   mkdir -p server_storage logs
   touch id_passwd.txt
   ```

---

## Usage

### Running the Server
1. Start the server:
   ```bash
   python server.py
   ```
2. The server listens on `127.0.0.1:8888` and logs activities in `logs/server.log`.

### Running the Client
1. Start the client:
   ```bash
   python client.py
   ```
2. Follow the prompts for authentication and file operations.

### Authentication
- Add user credentials in `id_passwd.txt` in the format:
  ```
  user1:hello1
  user2:hello2
  user3:hello3
  user4:hello4
  user5:hello5
  ```

### File Operations
1. **Upload**: Upload a file to the server.
2. **Download**: Download a file from the server.
3. **Preview**: View the first 1024 bytes of a file.
4. **Delete**: Remove a file from the server.
5. **List Directory**: View available files in the user's directory.
6. **Exit**: Disconnect from the server.

---

## File Descriptions
### Client Files
- **`client.py`**: Handles client-side operations, including server connection, authentication, and file operations.
- **`file_upload.py`**: Contains the logic to upload files to the server. (`upload_file` module)
- **`file_download.py`**: Handles file download from the server to the specified directory. (`download_file` module)
- **`file_preview.py`**: Implements the preview functionality for files(only first 1024 bytes). (`preview_file` module)

### Server Files
- **`server.py`**: Manages client connections, authentication, and file operations.
- **`file_upload.py`**: Receives uploaded files from clients. (`recv_file` module)
- **`file_download.py`**: Sends requested files to clients. (`send_file` module)
- **`file_preview.py`**: Reads and sends the first 1024 bytes of a file. (`send_preview` module)
- **`file_delete.py`**: Deletes files from the server. (`delete_file` module)

### Utility Files
- **`logger_util.py`**: Provides a setup for consistent logging across the client and server.

---

## Logging
- Logs are stored in the `logs` directory:
  - `client.log`: Client-side logs.
  - `server.log`: Server-side logs.
- Log levels: `INFO`, `DEBUG`, `WARNING`, and `ERROR`.

---

## Error Handling
- **Connection Errors**:
  - Handled by wrapping socket operations in try-except blocks.
  - Logs and displays errors such as connection timeouts or resets.
- **Invalid Input**:
  - Prompts users for valid inputs when incorrect choices are made.
- **Unauthorized Access**:
  - Ensures users can access only their files(validates the file path and give appropriate error message).
- **Timeouts**:
  - Automatically disconnects inactive clients after 100 seconds.

---




