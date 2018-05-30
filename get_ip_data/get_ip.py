import json
import logging
import os

import netifaces  # Getting ip address and subnet mast without any 3rd party library in python
# is very hacky, i would rather use a library than a hack.


def get_cidr(netmask):
    ''' get cidr( network size for a given subnet mask '''
    strcount = ''
    for octet in netmask:
        strcount += bin(int(octet))[2:].ljust(8, '0')
    strcount = len(strcount.rstrip('0'))
    logging.info(strcount)
    return str(strcount)


def get_ip_start(ipadd, netmask):
    ''' calculate start of ipaddress for a given subnet mask
        starting ip address is a( bitwise) AND operation between ip and subnet '''

    start_addr = [str(int(ipadd[index]) & int(netmask[index]))
                  for index in range(0, 4)]
    start_addr = '.'.join(start_addr)
    return start_addr


def get_ip_and_mask():
    ''' find all interfaces (IPV4) only as of now and calculate IP and CIDR '''

    interface_list = {}
    for adapter in netifaces.interfaces():
        ipaddr = netifaces.ifaddresses(adapter)[netifaces.AF_INET][0]['addr']
        subnetmask = netifaces.ifaddresses(
            adapter)[netifaces.AF_INET][0]['netmask']
        subnetmask = subnetmask.split('.')
        ipaddr = ipaddr.split('.')
        cidr = get_cidr(subnetmask)
        start_ip = get_ip_start(ipaddr, subnetmask)
        interface_list[adapter] = start_ip + "/" + cidr
    print json.dumps(interface_list, indent=4, sort_keys=True)


if __name__ == "__main__":
    get_ip_and_mask()
