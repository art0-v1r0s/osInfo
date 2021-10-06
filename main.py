import platform
import os
from subprocess import check_output
from xml.etree.ElementTree import fromstring
from ipaddress import IPv4Interface, IPv6Interface
import sys


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


if len(sys.argv) > 1:
    if sys.argv[1] == "-h":
        print(
            "###########################\n"
            "#         INFO            #\n"
            "#          OS             #\n"
            "###########################\n"
            "welcome in Info Os helper\n"
            "this programme put the network info in a file\n"
            "thanks to execute the programme\n"
        )
        exit()
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
print(OS)
if "Windows" in OS:
    print("it's Windows")
    fichier.write("OS : %s \n" % OS)
    nics = get_interfaces()
    for nic in nics:
        fichier.write('\n')
        for k, v in nic.items():
            fichier.write('%s : %s \n' % (k, v))
            #print('%s : %s' % (k, v))
fichier.close()

fichier = open("ipconfig.txt", "r")
lignes = fichier.readlines()

choix = switch()
for ligne in lignes:
    if choix in ligne:
        print(ligne)
fichier.close()
# ligne = ip.readline()
