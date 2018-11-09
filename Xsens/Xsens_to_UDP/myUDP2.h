#include <QObject>
#include <QUdpSocket>

class myUDP2 : public QObject
{
	Q_OBJECT

public:
	myUDP2(QObject *parent =  0);
	~myUDP2();
	void sendDataFormated(QString deviceID, QString strDataType, QString dateTime, QString strData);

	void setUdpIp(QHostAddress udp_ip_new) { udp_ip = udp_ip_new; };
	void setUdpPort(int udp_port_new) { udp_port = udp_port_new; };
	QHostAddress getUdpIp() { return udp_ip; };
	int getUdpPort() { return udp_port; };

private:
	QUdpSocket *socket;
	QHostAddress udp_ip = QHostAddress::LocalHost;
	int udp_port = 12345;
};