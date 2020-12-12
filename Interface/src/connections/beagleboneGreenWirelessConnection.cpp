// Date: December 2020
// Requirements: c++11
// Arguments needed for compilation: ["-std=c++11", "-pthread"] 

// -*- SoftWEAR Communications module. C++ API -*- 

#include <iostream>
#include <string>
#include <unistd.h>
#include <vector>               // Vectors for sending and receving queues
#include <chrono>               // Threading time managment
#include <sys/socket.h>         // Definitions for internet operations
#include <arpa/inet.h>          // Socket con
#include <thread>               // Thread module to send and receive messages in parallel 
#include <sstream>              // Used for socket reading, sending and string spliting
#include <nlohmann/json.hpp>    // Serializing module 

using namespace std;
using json = nlohmann::json;

vector<string> split(string str, char delimiter) {
    /**
     * Construct a vector of sub-strings from given string.
     * Sub-string comes from the delimiter-separated string.
     * If delimiter is at the end of the string, add an empty string to the vector.
     * @str is the string to split base on delimiter @delimiter.
     * Uses sstream library.
     */
    vector<string> tokens;                          // Vector of string to save tokens
    stringstream check1(str);                       // stringstream class check1 
    string intermediate; 
      
    while(getline(check1, intermediate, delimiter)) // Tokenizing w.r.t. delimiter
        tokens.push_back(intermediate);

    if (str.back() == delimiter)                    
        tokens.push_back("");                       // Add empty string to vector if delimiter is at the end (like Python split)

    return tokens;
}

class beagleboneGreenWirelessConnection {
    public:
        string ip;                                              // The IP of the remote location
        int port;                                               // The Application Port

        beagleboneGreenWirelessConnection() {                   // Class constructor 1
            ip = "192.168.7.2";
            port = 12345; 
        }
        beagleboneGreenWirelessConnection(string ip) {          // Class constructor 2
            this->ip = ip;
            port = 12345;
        }
        beagleboneGreenWirelessConnection(string ip, int port){ // Class constructor 3
            this->ip = ip;
            this->port = port;            
        }

        void open();
        void shutdown();
        void sendMessages(json messages);
        json getMessages();

    private:
        vector<string> sendQueue;                               // Sending queue
        vector<string> recvQueue;                               // Receiving queue
        bool running=true;                                      // Inner communications thread object
        int sock;                                               // TCP client
        void inner_thread();
};

void beagleboneGreenWirelessConnection::sendMessages(json messages) {
    /**
     * Send a json object to the remote host.
     * @messages is an array of json objects.
     * Uses json module.
     */
    for (json::iterator message = messages.begin(); message != messages.end(); ++message)
        sendQueue.push_back((*message).dump());
}

json beagleboneGreenWirelessConnection::getMessages() {
    /**
     * Construct an array of json objects based on strings in @recvQueue.
     * Returns an array of json objects.
     * Uses json module.
     */
json messages;                                              // Initialize json array
while (!recvQueue.empty()) {                                // Pop all messages from the receiving queue and add them to the return array
        messages.push_back(json::parse(recvQueue[0]));      // Add json parsed strings to the json array
        recvQueue.erase(recvQueue.begin());                 // Pop the receiving queue
    }
return messages;
}

void beagleboneGreenWirelessConnection::open() {
    /**
     * Build socket and initialize connection to remote host.
     * Uses socket module.
     */
    struct sockaddr_in serv_addr;                                               // Socket adress information

    if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0) {                         // Check if socket is valid
        printf("\n Socket creation error \n"); 
        exit(EXIT_FAILURE);
    } 
    serv_addr.sin_family = AF_INET;                                             // Fill socket information
    serv_addr.sin_port = htons(port); 

    if(inet_pton(AF_INET, ip.c_str(), &serv_addr.sin_addr)<=0) {                // Convert IPv4 and IPv6 addresses from text to binary form 
        printf("\nInvalid address/ Address not supported \n"); 
        exit(EXIT_FAILURE);
    } 
    if (connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) {  // Connect to remote host
        printf("\nConnection Failed \n"); 
        exit(EXIT_FAILURE);
    }
    running = true;                                                             // Start thread
    thread th1(&beagleboneGreenWirelessConnection::inner_thread, this); 
    th1.detach();                                                               // Detached mode thread
}

void beagleboneGreenWirelessConnection::shutdown() {
    /**
     * Close connection and terminate thread
     */
    this_thread::sleep_for(chrono::seconds(1));     // Wait that all messages are sent 
    running = false;                                // Terminate thread
    if (close(sock) < 0)                            
        printf("\nClosing Failed \n"); 
}

void beagleboneGreenWirelessConnection::inner_thread() {
    /**
     * Main thread that handles messages sending and receiving.
     * Data is received by packets of 1024 bytes.
     * Data received has to be parsed manually to find completed json objects.
     */
    int valread;                                    // Result of reading (not used)
    char buffer[1032] = {0};                        // Buffer for received data, 1 supplementary byte to avoid overflow
    vector<string> m_vector;                        // Vector of splited strings
    string remainder = "";                          // Memorize uncomplete messages
    string send_message;                            // Message to send

    while(running) {
        memset(buffer,0, strlen(buffer));           // Empty buffer (keeps previous message otherwise)
        valread = read(sock , buffer, 1024);        // Receives data

        if (!valread)                               // Connection closed
            break;
        m_vector = split(remainder + buffer, '}');  // Add memorized buffers and split
        remainder = "";

        while (m_vector.size() > 0) {               // Append data to @remainder until a complete message is found
            // Case where @remainder doesn't contain a complete messgage (more '{' than '}')
            if (!remainder.empty() && (count(remainder.begin(), remainder.end(), '{') > 
                                       count(remainder.begin(), remainder.end(), '}'))) { 
                remainder += m_vector[0];           // Append to remainder
                m_vector.erase(m_vector.begin());
                if (m_vector.size() > 0)            // Don't put a closing bracket on last element of vector because uncomplete
                    remainder += "}";               // Add closing bracket (lost during split operation)
            }
            // Case where @remainder contains a complete message
            else if (!remainder.empty()) {          
                recvQueue.push_back(remainder);     // Add message to receiving queue
                remainder = "";                     // Clear @remainder
            }
            // Case where the only element of vector is an empty list (means that } was the last character)
            else if (m_vector.size() == 1 && m_vector[0] == "")
                m_vector.erase(m_vector.begin());
            // Case where we have no message and the list is not empty -> start a new sub-message
            else {
                remainder += m_vector[0];
                m_vector.erase(m_vector.begin());
                if (m_vector.size() > 0)
                    remainder += "}";
            }
        }
        while (sendQueue.size() > 0) {              // Pop all elements from the sending queue and send them all
            send_message = sendQueue[0];
            sendQueue.erase(sendQueue.begin());
            send(sock, send_message.c_str(), strlen(send_message.c_str()), 0);
        }
    }
}

int main(int argc, char const *argv[]) {
    /**
     * Test @beagleboneGreenWirelessConnection class.
     * Send and receive json objects.
     * Give examples.
     */

    // Array of two json objects to send
    json m = {
        {
            {"type", "Settings"},
            {"name", "PCA9685@I2C[1]"},
            {"dutyFrequency", "50 Hz"}
        },
        {
            {"type", "Settings"},
            {"name", "PCA9685@I2C[1]"},
            {"dutyFrequency", "100 Hz"}
        }
    };

    // Another way to construct json objects
    m.clear();

    json m1 = {
        {"type", "Settings"},
        {"name", "PCA9685@I2C[1]"},
        {"dutyFrequency", "50 Hz"}
    };
    
    json m2 = {
        {"type", "Settings"},
        {"name", "PCA9685@I2C[1]"},
        {"dutyFrequency", "50 Hz"}
    };

    m.push_back(m1);                                                // Add json object
    m.push_back(m2);                                                // Add json object

    // Start
    beagleboneGreenWirelessConnection c ("192.168.7.2", 12345);     // Constructor (arguments optional)
    c.open();                                                       // Connect and start thread

    c.sendMessages(m);                                              // Sends the json messages
    
    this_thread::sleep_for(chrono::seconds(1));                     // Wait to receive some messages
    json messages = c.getMessages();                                // Get json object type messages
    cout << messages[0] << "\n";                                    // Example of a json object message
    cout << messages[0]["data"][0]["name"];                         // Example of how to access values

    c.shutdown();                                                   // Terminate thread and close connection
    
    return 0;
}