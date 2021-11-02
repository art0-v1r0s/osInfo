import platform
import os
import socket
import threading
from subprocess import check_output
from xml.etree.ElementTree import fromstring
from ipaddress import IPv4Interface, IPv6Interface
import sys



host = {}
""" classe définissant le thread de scan d'adresse Ip servant à récupérer """
""" le hostname du périphérique réseau                                    """


class NetscanThread(threading.Thread):
    """ Constructeur de la classe prend en argument les paramètres suivants: """
    """ address : adresse IP à scanner                                       """

    def __init__(self, address):

        self.address = address
        threading.Thread.__init__(self)

    """ Définition de la méthode Run de notre classe de scan """

    def run(self):
        self.lookup(self.address)

    """ Méthode de classe permettant de récupérer le hostname du périphérique           """
    """ connecté au réseau. Elle prend en paramètrre la variable de classe représentant """
    """ l'adresse IP à recherchée                                                       """

    def lookup(self, address):

        """ On gère l'exception en cas de périphérique non connecté à l'adresse IP à scanner """
        try:
            """ On récupère le hostname et l'alias de la machine connectée """
            hostname, alias, _ = socket.gethostbyaddr(address)
            global host
            """ On associe le hostname à l'adresse IP et on les sauve dans le dictionnaire """
            host[address] = hostname
        except socket.herror:
            host[address] = None


def get_interfaces():
    cmd = 'wmic.exe nicconfig where "IPEnabled  = True" get ipaddress,MACAddress,IPSubnet,DNSHostName,Caption,DefaultIPGateway /format:rawxml'
    xml_text = check_output(cmd, creationflags=8)
    xml_root = fromstring(xml_text)

    nics = []
    keyslookup = {
        'DNSHostName': 'hostname',
        'IPAddress': 'ip',
        'IPSubnet': '_mask',
        'Caption': 'hardware',
        'MACAddress': 'mac',
        'DefaultIPGateway': 'gateway',
    }

    for nic in xml_root.findall("./RESULTS/CIM/INSTANCE"):
        # parse and store nic info
        n = {
            'hostname': '',
            'ip': [],
            '_mask': [],
            'hardware': '',
            'mac': '',
            'gateway': [],
        }
        for prop in nic:
            name = keyslookup[prop.attrib['NAME']]
            if prop.tag == 'PROPERTY':
                if len(prop):
                    for v in prop:
                        n[name] = v.text
            elif prop.tag == 'PROPERTY.ARRAY':
                for v in prop.findall("./VALUE.ARRAY/VALUE"):
                    n[name].append(v.text)
        nics.append(n)

        # creates python ipaddress objects from ips and masks
        for i in range(len(n['ip'])):
            arg = '%s/%s' % (n['ip'][i], n['_mask'][i])
            if ':' in n['ip'][i]:
                n['ip'][i] = IPv6Interface(arg)
            else:
                n['ip'][i] = IPv4Interface(arg)
        del n['_mask']

    return nics


def switch():
    option = int(input("Que souhaitez vous recuperé : \n"
                       "1 : Hostname\n"
                       "2 : Ip\n"
                       "3 : Hardware\n"
                       "4 : Mac\n"
                       "5 : Gateway\n"))
    if option == 1:
        result = "hostname :"
        return result

    elif option == 2:
        result = "ip :"
        return result

    elif option == 3:
        result = "hardware :"
        return result

    elif option == 4:
        result = "mac :"
        return result

    elif option == 5:
        result = "gateway :"
        return result

    else:
        print("Incorrect option")


if len(sys.argv) >= 1:
    if "-h" in sys.argv:
        print(
            "###########################\n"
            "#         INFO            #\n"
            "#          OS             #\n"
            "###########################\n"
            "welcome in Info Os helper\n"
            "this programme put the network info in a file\n"
            "thanks to execute this programme\n"
        )
        exit()
    if "-s" in sys.argv:
        print("vous avez saisie l'argument s")
        host = {}
        addresses = []

        """ On définit une plage d'adresses IP à scanner """
        network = input("entre le reseau que vous souhaitez scanner (192.168.1.) :")
        for ping in range(1, 254):
            addresses.append(network + str(ping))

        threads = []

        """ On créée autant de threads qu'il y à d'adresses IP à scanner """
        netscanthreads = [NetscanThread(address) for address in addresses]
        for thread in netscanthreads:
            """ Chaque thread est démarré en même temps """
            thread.start()
            threads.append(thread)

        for t in threads:
            t.join()

        """ On affiche le résultat qui affiche pour chaque machine connectée son nom d'hôte """
        try:
            with open('scanIP.txt'):
                pass
        except IOError:
            lecteurIP = input("Si le fichier n'est pas a la racine du fichier peut -on le recré [O/N] : ")
            if lecteurIP == "N":
                exit()

        fichierIP = open("scanIP.txt", 'w')
        for address, hostname in host.items():
            if (hostname != None):
                print(address, '=>', hostname)
                """
                #BEAUCOUP TROP LONG
                try:
                    for port in range(1, 1025):
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        result = sock.connect_ex((address, port))
                        if result == 0:
                            print("Port {}: 	 Open".format(port))
                        sock.close()
                except socket.error:
                    print
                    "Couldn't connect to server"
                    sys.exit()
                    """

                if "-o" in sys.argv:
                    """ On ecrit dans le fichier le resultat de l'operation """
                    fichierIP.write('%s => %s \n' % (address, hostname))
        fichierIP.close()

for root, directories, files in os.walk("."):
    for file in files:
        print(file)
try:
    with open('ipconfig.txt'):
        pass
except IOError:
    lecteur = input("Si le fichier n'est pas a la racine du fichier peut -on le recré [O/N] : ")
    if lecteur == "N":
        exit()

fichier = open("ipconfig.txt", 'w')
OS = platform.system()
# print(OS)
if "Windows" in OS:
    print("it's Windows")
    fichier.write("OS : %s \n" % OS)
    nics = get_interfaces()
    for nic in nics:
        fichier.write('\n')
        for k, v in nic.items():
            fichier.write('%s : %s \n' % (k, v))
            # print('%s : %s' % (k, v))
fichier.close()

fichier = open("ipconfig.txt", "r")
lignes = fichier.readlines()

choix = switch()
for ligne in lignes:
    if choix in ligne:
        print(ligne)
fichier.close()
# ligne = ip.readline()
