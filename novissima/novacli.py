#!/usr/bin/env python 


import commands
import os
import pwd
import sys
import time


from novissima import novacore


class NovaCLI:

    def __init__(self):
    
        try:
            self._setenvironment()
        except KeyError, k:
            print('mandatory variable %s is not defined in the environment', k)
            raise Exception
        self.core = novacore.NovaCore(self.VERSION, self.USERNAME, self.PASSWORD, self.PROJECT_ID, self.AUTH_URL)

        class BColors:
            HEADER = '\033[95m'
            OKBLUE = '\033[94m'
            OKGREEN = '\033[92m'
            WARNING = '\033[93m'
            FAIL = '\033[91m'
            ENDC = '\033[0m'
            BOLD = '\033[1m'
            UNDERLINE = '\033[4m'
        self.bcolors = BColors()


    def _setenvironment(self):

        self.VERSION = "2" 
        self.USERNAME = os.environ['OS_USERNAME']
        self.PASSWORD = os.environ['OS_PASSWORD']
        self.PROJECT_ID = os.environ['OS_TENANT_NAME']
        self.AUTH_URL = os.environ['OS_AUTH_URL']


    # -------------------------------------------------------------------------
    #       public interface
    # -------------------------------------------------------------------------


    def usage(self):

        print('')
        print('Tool to facilitate instantiating a VM with nova.')
        print('Usage:')
        print('')
        print('$ python get_nova_vm_api.py create|delete')
        print('')


    def create(self):
    
        self.image = self._set_image()
        self.vm_name = self._set_vm_name()
        self.flavor = self._set_flavor()
        self.server = self._create()
        self.fixed_ip = self._set_ip()
        self._print_login_message()





    def delete(self):
    
        list_servers = self.core.get_list_servers()
        list_servers.sort(novacore.sort_by_name)
        index = self._select_server_to_delete_from_list(list_servers)
        server = list_servers[index-1]
        print("Deleting VM instance with name %s ..." %server.name)
        self.core.delete_server(server)
        print("VM instance with name %s deleted" %server.name)





    # -------------------------------------------------------------------------


    def _set_image(self):
        list_images = self.core.get_list_images()
        list_images.sort(novacore.sort_by_name)
        index = self._select_image_from_list(list_images)
        image = list_images[index-1]
        return image


    def _set_vm_name(self):

        username = pwd.getpwuid( os.getuid() )[ 0 ] 
        date = time.strftime('%y%m%d')
        default_vm_name = "%s-%s-%s" %(self.image.name, username, date)
        vm_name = raw_input("Type a name for the VM instance (or hit ENTER for suggested name: %s) " %default_vm_name )
        if not vm_name:
            vm_name = default_vm_name
        return vm_name


    def _set_flavor(self):

        #flavor = self.nova.flavors.find(name='m1.medium')
        # FIXME:
        #   make 'm1.medium' the default
        list_flavors = self.core.get_list_flavors()
        list_flavors.sort(novacore.sort_by_name)
        index = self._select_flavor_from_list(list_flavors)
        flavor_name = list_flavors[index-1].name
        flavor = self.core.get_flavor(flavor_name)
        return flavor


    def _select_image_from_list(self, list_images):
        return self._select_from_list(list_images, "VM images")

    
    def _select_flavor_from_list(self, list_flavors):
        return self._select_from_list_extended(list_flavors, "image flavors", ['vcpus', 'disk', 'ram'])

    
    def _select_server_to_delete_from_list(self, list_servers):
        return self._select_from_list(list_servers, "VM instances (servers) currently running")


    def _select_from_list(self, list_items, item_type):
        """
        generic method to display a list of options 
        on the stdout, 
        and let the user to pick one by index number
        """

        print("List of available %s:" %item_type)
        for i in range(len(list_items)):
            print("    %s%s %s%s : %s%s" %(self.bcolors.BOLD, self.bcolors.FAIL, i+1, self.bcolors.OKBLUE, list_items[i].name, self.bcolors.ENDC))
        index = raw_input("Pick one by typing the index number: ")
        index = int(index)
        return index

    # FIXME
    # temporary solution
    # this needs to be merged with _select_from_list()
    def _select_from_list_extended(self, list_items, item_type, list_attributes):
        """
        generic method to display a list of options 
        on the stdout, 
        and let the user to pick one by index number
        """

        print("List of available %s:" %item_type)
        for i in range(len(list_items)):
            out = "    %s%s %s%s " %(self.bcolors.BOLD, self.bcolors.FAIL, i+1, self.bcolors.OKBLUE)
            out += ": %s " %list_items[i].name
            out += ' '*(20 - len(list_items[i].name) - len(str(i+1)))
            for attr in list_attributes:
                token = " %s=%s " %(attr, list_items[i].__dict__[attr])
                out += token
                out += " "*(10 - len(token))
            out += " %s" %self.bcolors.ENDC
            print(out)
        index = raw_input("Pick one by typing the index number: ")
        index = int(index)
        return index


    def _create(self):

        print("Instantiating VM %s ... (it may take a few seconds)" %self.vm_name)
        server = self.core.create_server(self.vm_name, self.image, flavor=self.flavor)
        self.server_id = server.id
        print("VM %s instantiated, with ID %s" %(self.vm_name, self.server_id))
        return server


    def _set_ip(self):

            return self.core.set_fixed_ip(self.server)


    def _print_login_message(self):

        print("now you can log into your new VM with command:")
        print("     ssh root@%s" %self.fixed_ip.ip)
        print("")
        print("when finished, delete the VM with commands:")
        print("     nova floating-ip-disassociate %s %s" %(self.server_id, self.fixed_ip.ip))
        print("     nova stop %s" %self.server_id)
        print("     nova delete %s" %self.server_id)
        print("or running this script with 'delete' option")
        print("")


# =========================================================================

if __name__ == '__main__':

    # FIXME!!
    # this needs to be done properly, with argparse, getopt, or similar.

    try:
        cli = NovaCLI()
    except:
        # FIXME
        pass
        
    if len(sys.argv) != 2:
        cli.usage()
        sys.exit()    
    
    if sys.argv[1] == 'create':
        cli.create()
    elif sys.argv[1] == 'delete':
        cli.delete()
    else:
        #FIXME
        sys.exit()    
