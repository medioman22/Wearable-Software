#include "myUDP2.h"

myUDP2::myUDP2(QObject *parent)
	: QObject(parent)
{
	socket = new QUdpSocket(this);

	//We need to bind the UDP socket to an address and a port
	//socket->bind(udp_ip, udp_port);         //ex. Address localhost, port 12346
}
myUDP2::~myUDP2()
{
}

void myUDP2::sendDataFormated(QString deviceID, QString strDataType,QString dateTime, QString strData)      //Just spit out some data
{
	QByteArray Data;
	Data.append("Xsens[");
	Data.append(deviceID);
	Data.append("], ");
	Data.append(strDataType);
	Data.append(", ");
	Data.append(dateTime);
	Data.append(", ");
	Data.append(strData);

	socket->writeDatagram(Data, udp_ip, udp_port);

	//If you want to broadcast something you send it to your broadcast address
	//ex. 192.2.1.255
}