/**
 * Responsible for thread-safe mailbox storage and management.
 * This class acts as the central shared resource that all ClientHandler threads 
 * access to store, retrieve, or delete messages.
 * 
 * Connection to the rest of the project:
 * Created once by Server.java and passed to every ClientHandler.
 * MUST use synchronization (e.g., synchronized blocks/methods or concurrent data structures)
 * to prevent race conditions.
 */
public class SharedMailbox {

    // Placeholder fields
    // private Map<String, List<Message>> userInboxes; // Maps a username to their messages

    public SharedMailbox() {
        // Initialization logic goes here
    }

    /**
     * Thread-safe method to add a message to one or multiple users' inboxes.
     * Supports the feature: sending messages to multiple people.
     */
    public synchronized void saveMessage(Message message) {
        // Iterate through message receivers and add to their respective inboxes
    }

    /**
     * Thread-safe method to retrieve messages for a specific user.
     * Supports the feature: reading messages.
     */
    public synchronized /* List<Message> */ void getMessagesForUser(String username) {
        // Return a copy of the user's messages to prevent concurrent modification issues
    }

    /**
     * Thread-safe method to delete a specific message from a user's inbox.
     * Supports the feature: deleting messages.
     */
    public synchronized void deleteMessage(String username, int messageId) {
        // Locate and remove the specified message
    }
}
