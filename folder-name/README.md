# Terminal-Based Mailbox System

## Overview
This project is a terminal-based mailbox system built in Java, developed as an Operating Systems group project. It expands upon a basic client-server architecture to provide a robust, multi-user messaging system. The focus is on demonstrating core Operating System concepts such as networking (sockets), multithreading, synchronization, and the safe handling of shared resources.

This project is meant to be run entirely from the terminal (command line) and does not rely on graphical interfaces (GUI/Swing/JavaFX), web frontend, or external databases.

## Features
* **Multi-Client Support**: Allows multiple clients to connect to the server at the same time using dedicated threads for each connection.
* **Send Messages to Multiple People**: Users can broadcast a single message to several different recipients at once.
* **Message Management**: Users have full control over their inboxes, with the ability to read, save/store, and delete their messages.
* **Persistent Storage**: Mailbox data is saved to the disk, meaning messages and user accounts are not lost when the server goes offline or is restarted.
* **Thread-Safe Shared Data**: The central mailbox is built using proper synchronization techniques, ensuring that concurrent operations (like multiple users sending/reading/deleting messages at the exact same time) happen reliably without causing data corruption or race conditions.
