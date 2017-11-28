#!/usr/bin/env python 

#
# documentation on the python API:
#       http://docs.openstack.org/developer/python-novaclient/ref/v2/
#

#
#  NOTE
#   interactive tests
#   
#   $ cd /usr/lib/python2.6/site-packages/novaclient
#   $ python
#   >>> 
#   >>> import os
#   >>> import pwd 
#   >>> import sys 
#   >>> import time
#   >>> 
#   >>> VERSION = "2" 
#   >>> USERNAME = os.environ['OS_USERNAME']
#   >>> PASSWORD = os.environ['OS_PASSWORD']
#   >>> PROJECT_ID = os.environ['OS_TENANT_NAME']
#   >>> AUTH_URL = os.environ['OS_AUTH_URL']
#   >>> 
#   >>> import client
#   >>> nova = client.Client(VERSION, USERNAME, PASSWORD, PROJECT_ID, AUTH_URL)
#   >>> 
#   >>> print nova.flavors.list()
#   ...
#

__version__ = "0.9.1"


import commands
import os
import pwd
import sys
import time

# FIXME: 
# what to do if the import fails?
from novaclient import client as novaclient



# =========================================================================

def sort_by_name(x, y):
    """
    function to sort list of Items by their attribute .name
    """
    if x.name < y.name: return -1
    if x.name == y.name: return 0
    if x.name > y.name: return 1


# =========================================================================

class NovaCore:

    def __init__(self, *k, **kw):
        self.client = novaclient.Client(*k, **kw)
        # examples of a call to this __init__ method
        #
        # 1.
        #       VERSION = "2"
        #       USERNAME = os.environ['OS_USERNAME']
        #       PASSWORD = os.environ['OS_PASSWORD']
        #       PROJECT_ID = os.environ['OS_TENANT_NAME']
        #       AUTH_URL = os.environ['OS_AUTH_URL']
        #       
        #       core = novacore.NovaCore(VERSION, USERNAME, PASSWORD, PROJECT_ID, AUTH_URL)
        #
        # 2. 
        #
        #       d = {'username' : USERNAME,
        #            'project_id' : PROJECT_ID,
        #            'project_name' : PROJECT_NAME,
        #            'password' : PASSWORD,
        #            'auth_url' : AUTH_URL,
        #            'user_domain_name' : USER_DOMAIN_NAME
        #           }
        #       
        #       core = novacore.NovaCore("2", **d)
        #

    def get_list_images(self):
    
        list_images = []
        for image in self.client.images.list():
            if image.status == "ACTIVE":
                list_images.append(image)
        return list_images


    def get_list_flavors(self):

        list_flavors = []
        for flavor in self.client.flavors.list():
            list_flavors.append(flavor)
        return list_flavors


    def get_list_servers(self):

        list_servers = []
        for server in self.client.servers.list():
            list_servers.append(server)
        return list_servers


    def get_image(self, image_name):
        return self.client.images.find(name=image_name)


    def get_flavor(self, flavor_name):
        return self.client.flavors.find(name=flavor_name)


    def get_server(self, server_name):
        return self.client.servers.find(name=server_name)


    def get_next_floating_ip(self): 

        list_floating_ips = self.client.floating_ips.list()
        # search for the first available IP not yet picked up
        for floating_ip in list_floating_ips:
            if not floating_ip.fixed_ip:
                return floating_ip


    def create_server(self, vm_name, image, flavor, **kw):
        '''
        boot a VM server in OpenStack
        vm_name: is the name that server will have
        image: image type to be booted. It can be a Image object of a string Image.name
        flavor: flavor type to be booted. It can be a Flavor object of a string Flavor.name
        '''

        if type(image) is str:
            image = self.get_image(image)
        if type(flavor) is str:
            flavor = self.get_flavor(flavor)
        server = self.client.servers.create(vm_name, image, flavor=flavor, **kw)
        self._wait_until_active(server)
        return server


    def _wait_until_active(self, server):
        '''
        wait in a loop until the server is in status ACTIVE
        '''
        while True:
            status = server.status
            power = int(server.__dict__['OS-EXT-STS:power_state'])
            if status == "ACTIVE" and power == 1:
                return 
            time.sleep(1)


    def delete_server(self, server):
        '''
        delete a VM server in OpenStack
        server: server to be deleted. It can be a Server object of a string Server.name
        '''
        if type(server) == str:       
            server = self.get_server(server)
        server.stop()
        server.delete()


    def set_fixed_ip(self, server):

        floating_ip = self.get_next_floating_ip() 
        return self.add_floating_ip(server, floating_ip)
     
    
    def add_floating_ip(self, server, floating_ip): 

        self.client.servers.add_floating_ip(server, floating_ip.ip)
        fixed_ip = self.client.floating_ips.find(ip=floating_ip.ip)
        return fixed_ip

