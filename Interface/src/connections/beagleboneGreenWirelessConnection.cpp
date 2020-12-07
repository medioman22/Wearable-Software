// Date: December 2020
// Requirements: c++11
// Arguments for compilation: ["-std=c++11", "-pthread"] 

/*** SoftWEAR Communications module. C++ API ***/

#include <iostream>
#include <string>
#include <unistd.h>
#include <chrono>
#include <vector>
#include <sys/socket.h> 
#include <arpa/inet.h> 
#include <thread> 
#include <sstream>
#include <algorithm>

using namespace std;

vector<string> split(string str, char delimiter) {
    // Vector of string to save tokens 
    vector <string> tokens; 
    // stringstream class check1 
    stringstream check1(str); 
      
    string intermediate; 
      
    // Tokenizing w.r.t. space ' ' 
    while(getline(check1, intermediate, delimiter)) 
        tokens.push_back(intermediate);

    return tokens;
}

class beagleboneGreenWirelessConnection {
    public:
        // % The IP of the remote location
        string ip;

        // The Application Port
        int port;

        // Class constructor
        beagleboneGreenWirelessConnection(){
            ip = "192.168.7.2";
            port = 12345; 
        }

        // Class constructor 2
        beagleboneGreenWirelessConnection(string ip){
            this->ip = ip;
            port = 12345;
        }

        // Class constructor 3
        beagleboneGreenWirelessConnection(string ip, int port){
            this->ip = ip;
            this->port = port;            
        }

        void open();
        void shutdown();
        void sendMessages(vector<string> messages);
        vector<string> getMessages();

    private:
        // Send queue
        vector<string> sendQueue;

        // Recv queue
        vector<string> recvQueue;

        //Inner communications thread object
        bool running=true;

        // tcp client
        int sock;

        void inner_thread();

        
};

void beagleboneGreenWirelessConnection::sendMessages(vector<string> messages) {
    /* Send a data object to the remote host */
    for (auto message = messages.begin(); message != messages.end(); ++message)
        sendQueue.push_back(*message);
    
}

vector<string> beagleboneGreenWirelessConnection::getMessages() {
    /* Get a list of all the messages that have been recieved since the last call of this function */
    vector<string> messages;                                 // return object initialized as an empty list
    while (!messages.empty()) {                              // Pop all messages from the recieve queue and add them to the return list
        messages.push_back(recvQueue[0]);
        recvQueue.erase(messages.begin());
    }
    return messages;                                         // Messages returned need to be stringified JSON objects
}

void beagleboneGreenWirelessConnection::open() {
    // socket adress information
    struct sockaddr_in serv_addr; 

    if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0) { 
        printf("\n Socket creation error \n"); 
        exit(EXIT_FAILURE);
    } 

    serv_addr.sin_family = AF_INET; 
    serv_addr.sin_port = htons(port); 

    // Convert IPv4 and IPv6 addresses from text to binary form 
    if(inet_pton(AF_INET, ip.c_str(), &serv_addr.sin_addr)<=0) { 
        printf("\nInvalid address/ Address not supported \n"); 
        exit(EXIT_FAILURE);
    } 

    if (connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) { 
        printf("\nConnection Failed \n"); 
        exit(EXIT_FAILURE);
    } 

    running = true;
    thread th1(&beagleboneGreenWirelessConnection::inner_thread, this); 
    th1.detach();
}

void beagleboneGreenWirelessConnection::shutdown() {
    this_thread::sleep_for(chrono::seconds(1));
    running = false;
    if (close(sock) < 0)
        printf("\nClosing Failed \n"); 
}

void beagleboneGreenWirelessConnection::inner_thread() {
    int valread;
    char buffer[1024] = {0}; 
    vector<string> m_list;
    string remainder = "";
    string send_message;

    while(running) {

        try {
            valread = read(sock , buffer, 1024);
            if (!valread) break;
            m_list = split(remainder + buffer, '}');
            remainder = "";
            while (m_list.size() > 0) {
                if (!remainder.empty() && (count(remainder.begin(), remainder.end(), '{') > 
                                           count(remainder.begin(), remainder.end(), '}'))) { 
                    remainder += m_list[0];
                    m_list.erase(m_list.begin());
                    if (m_list.size() > 0)
                        remainder += "}";
                }
                else if (!remainder.empty()) {
                    recvQueue.push_back(remainder);
                    remainder = "";
                }
                else if (m_list.size() == 1 && m_list[0] == "")
                    m_list.erase(m_list.begin());
                else {
                    remainder += m_list[0];
                    m_list.erase(m_list.begin());
                    if (m_list.size() > 0)
                        remainder += "}";
                }
            }
        }
        catch (...) {
            cout << "Error getting messages";
        }
        while (sendQueue.size() > 0) {
            cout << "fwef";
            send_message = sendQueue[0];
            sendQueue.erase(sendQueue.begin());
            send(sock, send_message.c_str(), strlen(send_message.c_str()), 0);
        }
    }
}

// Test
int main(int argc, char const *argv[]) {

    vector<string> message = {"{\"type\": \"Settings\", \"name\": \"PCA9685@I2C[1]\", \"dutyFrequency\": \"50 Hz\"}"};
    beagleboneGreenWirelessConnection c ("192.168.7.2", 12345);
    c.open();
    c.sendMessages(message);
    c.shutdown();
    return 0;
}