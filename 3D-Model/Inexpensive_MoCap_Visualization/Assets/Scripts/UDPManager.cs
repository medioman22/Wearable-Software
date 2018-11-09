/*

Author: Victor Faraut
Date: 28.10.2018


*/


using UnityEngine;
using System.Collections;

using System;
using System.Net;
using System.Net.Sockets;
using System.Text;

using System.Threading;
using System.Collections.Generic;
//using System.Globalization;

public class UDPManager : MonoBehaviour
{
    Vector3 currentRotVect = new Vector3(0, 0, 0);
    public int listenPort;
    public string IP = "127.0.0.1";

    private Thread t;
    private UdpClient listener;
    //private bool msgFromThread = false;
    private string msgName;
    private object msgPayload;

    public GameObject cube;
    public CubeMover cubemover;

    private char[] charSeparators = new char[] { ',' };

    void Start()
    {
        t = new Thread(new ThreadStart(ListenThread));
        //cubemover = cube.GetComponent<CubeMover>();
        t.IsBackground = true;
        t.Start();
    }

    void ListenThread()
    {
        listener = new UdpClient(listenPort);
        IPEndPoint groupEP = new IPEndPoint(IPAddress.Parse(IP), listenPort);
        string dat;
        string[] dataSplited;
        byte[] receive_byte_array;
        Debug.Log("Listener: Waiting for broadcasts...\n");
        while (true)
        {
            receive_byte_array = listener.Receive(ref groupEP);
            dat = Encoding.ASCII.GetString(receive_byte_array, 0, receive_byte_array.Length);
            dataSplited = dat.Split(charSeparators, StringSplitOptions.None);
            Debug.Log("test");
            if (dat[0] == 'B')
            {
                if ((dataSplited[1].Equals("9"))||
                    (dataSplited[1].Equals("10"))||
                    (dataSplited[1].Equals("11")))
                {
                    Debug.Log((float.Parse(dataSplited[3])).ToString());
                    cubemover.SetAngleXYZ(Int32.Parse(dataSplited[1])-9, float.Parse(dataSplited[3]));
                    Debug.Log("test");
                }
            }
            if (dat[0] == 'X')
            {
                if ((dataSplited[1].Equals("1")) ||
                    (dataSplited[1].Equals("2")) ||
                    (dataSplited[1].Equals("3")))
                {
                    Debug.Log((float.Parse(dataSplited[3])).ToString());
                    cubemover.SetAngleXYZ(Int32.Parse(dataSplited[1]) - 9, float.Parse(dataSplited[3]));
                    Debug.Log("test");
                }
            }
        }
    }

    void Update()
    {
        
    }

    void OnApplicationQuit()
    {
        if (t.IsAlive) t.Abort();
        if (listener != null) listener.Close();
    }
}



/*
public class UDPManager : MonoBehaviour
{
    static UdpClient udp;
    Thread thread;

    public GameObject cube;
    public CubeMover cubemover;
    public int port; 


    static readonly object lockObject = new object();
    string returnData = "";
    bool precessData = false;

    void Start()
    {
        cubemover = cube.GetComponent<CubeMover>();
        thread = new Thread(new ThreadStart(ThreadMethod));
        thread.Start();
    }

    void Update()
    {
        if (precessData)
        {
            /*lock object to make sure there data is 
             *not being accessed from multiple threads at thesame time*/
/*lock (lockObject)
{
    precessData = false;
    cube.SendMessage("Move");
    // or
    cubemover.Move();

    //Process received data
    Debug.Log("Received: " + returnData);

    //Reset it for next read(OPTIONAL)
    returnData = "";
}
}
}

private void ThreadMethod()
{
udp = new UdpClient(port);
while (true)
{
IPEndPoint RemoteIpEndPoint = new IPEndPoint(IPAddress.Any, 0);

byte[] receiveBytes = udp.Receive(ref RemoteIpEndPoint);

/*lock object to make sure there data is 
*not being accessed from multiple threads at thesame time*/
/*lock (lockObject)
{
    returnData = Encoding.ASCII.GetString(receiveBytes);

    Debug.Log(returnData);
    if (returnData == "1\n")
    {
        //Done, notify the Update function
        precessData = true;
    }
}
}
}
}*/
