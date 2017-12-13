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
import datetime
import os
import pwd
import sys
import time

from novaclient import client as novaclient

from novasimmaex import NovissimaServerCreationFailure
from novasimmaex import NovissimaServerCreationTimeOut



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


    def get_list_servers(self, **kw):

#        list_servers = []
#        for server in self.client.servers.list():
#            list_servers.append(server)
#        return list_servers
        return self.client.servers.list(search_opts=kw)


    def get_image(self, **kw):
        """
        example:  get_image(name='centos7'
        """
        return self.client.images.find(**kw)


    def get_flavor(self, **kw):
        """
        example:  get_flavor(name='m1.medium'
        """
        return self.client.flavors.find(**kw)


    def get_server(self, **kw):
        return self.client.servers.find(**kw)


    def get_next_floating_ip(self): 

        list_floating_ips = self.client.floating_ips.list()
        # search for the first available IP not yet picked up
        for floating_ip in list_floating_ips:
            if not floating_ip.fixed_ip:
                return floating_ip


    def create_n_servers(self, n, vm_name, image, flavor, **kw):
        """
        try to create N identical servers
        returns the list of all servers that were actually created
        """
        server_l = []
        for i in range(n):
            try:
                server = self.create_server(vm_name, image, flavor, **kw)
                server_l.append(server)
            except Exception, ex:
                pass
            else:
                server_l.append(server)
        return server_l 


    def create_server(self, vm_name, image, flavor, **kw):
        '''
        boot a VM server in OpenStack
        vm_name: is the name that server will have
        image: image type to be booted. It can be a Image object of a string Image.name
        flavor: flavor type to be booted. It can be a Flavor object of a string Flavor.name
        '''
        # get the timeout from the dictionary **kw, default is 5 minutes
        timeout = kw.pop('timeout', 300)
        
        # create the VM
        try:
            server = self.client.servers.create(vm_name, image=image, flavor=flavor, **kw)
        except Exception, ex:
            raise ex

        # wait until the VM is active
        try:
            self._wait_until_active(server, timeout)
            return server
        except Exception, ex:
            if server:
                server.delete()
            raise ex


    def _wait_until_active(self, server, timeout):
        '''
        in a loop until the server is in status ACTIVE
        '''
        id = server.id
        now = datetime.datetime.now()
        delta = 0
        keep = True
        while keep:
            server = self.get_server(id=id)
            status = server.status
            power = int(server.__dict__['OS-EXT-STS:power_state'])
            if status == "ACTIVE" and power == 1:
                keep = False
            else:
                delta = (datetime.datetime.now() - now).seconds
                if delta > timeout:
                    keep = False
        if delta > timeout:
           raise NovissimaServerCreationTimeOut('create_server', timeout)



    def remove_server(self, server):
        '''
        delete a VM server in OpenStack
        '''
        if type(server) == str:       
            server = self.get_server(name=server)
        server.stop()
        server.delete()


    def set_fixed_ip(self, server):

        floating_ip = self.get_next_floating_ip() 
        return self.add_floating_ip(server, floating_ip)
     
    
    def add_floating_ip(self, server, floating_ip): 

        self.client.servers.add_floating_ip(server, floating_ip.ip)
        fixed_ip = self.client.floating_ips.find(ip=floating_ip.ip)
        return fixed_ip

