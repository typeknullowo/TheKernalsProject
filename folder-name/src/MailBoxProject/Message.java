/**
 * Represents a single message in the mailbox system.
 * This is a simple data object (POJO) used to encapsulate message details 
 * such as the sender, receivers, content, and timestamp.
 * 
 * Connection to the rest of the project:
 * ClientHandlers will create Message objects when a "send" command is received.
 * The SharedMailbox will store and manage these Message objects.
 */
public class Message {

    // Placeholder fields
    // private String sender;
    // private List<String> receivers; // For sending messages to multiple people
    // private String content;
    // private long timestamp;

    /**
     * Constructor for creating a new message.
     */
    public Message(/* String sender, List<String> receivers, String content */) {
        // Initialization logic goes here
    }

    // Placeholder getter and setter methods
    // public String getSender() { return sender; }
    // public List<String> getReceivers() { return receivers; }
    // public String getContent() { return content; }
    
    /**
     * Formats the message for display in the terminal.
     */
    @Override
    public String toString() {
        return "Message placeholder";
    }
}
