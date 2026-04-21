package SocketStuff;

import java.io.*;
import java.net.*;
import java.util.ArrayList;

public class Server {

    private static ArrayList<String> mailbox = new ArrayList<>();

    public static void main(String[] args) throws IOException {
        Socket client = null;
        ServerSocket sock = null;

        try {
            sock = new ServerSocket(5155);

            while (true) {
                client = sock.accept();

                Socket finalClient = client;

                new Thread(() -> {
                    try {
                        BufferedReader bin = new BufferedReader(
                                new InputStreamReader(finalClient.getInputStream()));

                        PrintWriter pout = new PrintWriter(
                                finalClient.getOutputStream(), true);

                        String message;

                        while ((message = bin.readLine()) != null) {

                            synchronized (mailbox) {
                                mailbox.add(message);
                            }

                            System.out.println("Received: " + message);

                            pout.println("Server received: " + message);

                            synchronized (mailbox) {
                                pout.println("Mailbox: " + mailbox.toString());
                            }
                        }

                        finalClient.close();

                    } catch (IOException e) {
                        System.err.println(e);
                    }
                }).start();
            }

        } catch (IOException ioe) {
            System.err.println(ioe);
        } finally {
            if (client != null) {
                client.close();
            }
            if (sock != null) {
                sock.close();
            }
        }
    }
}