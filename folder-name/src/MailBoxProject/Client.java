package SocketStuff;

import java.io.*;
import java.net.Socket;

public class Client {

    public static void main(String[] args) throws IOException {

        Socket sock = null;

        try {
            sock = new Socket("127.0.0.1", 5155);

            BufferedReader serverInput = new BufferedReader(
                    new InputStreamReader(sock.getInputStream()));

            PrintWriter serverOutput = new PrintWriter(
                    sock.getOutputStream(), true);

            BufferedReader userInput = new BufferedReader(
                    new InputStreamReader(System.in));

            Thread receiveThread = new Thread(() -> {
                try {
                    String line;
                    while ((line = serverInput.readLine()) != null) {
                        System.out.println("Server: " + line);
                    }
                } catch (IOException e) {
                    System.err.println(e);
                }
            });

            Thread sendThread = new Thread(() -> {
                try {
                    String userMessage;
                    while ((userMessage = userInput.readLine()) != null) {
                        serverOutput.println(userMessage);
                    }
                } catch (IOException e) {
                    System.err.println(e);
                }
            });

            receiveThread.start();
            sendThread.start();

            receiveThread.join();
            sendThread.join();

        } catch (IOException | InterruptedException ioe) {
            System.err.println(ioe);
        } finally {
            if (sock != null) {
                sock.close();
            }
        }
    }
}