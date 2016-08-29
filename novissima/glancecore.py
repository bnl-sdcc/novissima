#!/usr/bin/env python 

#
# documentation on the python API:
#       http://docs.openstack.org/developer/python-novaclient/ref/v2/
#

#
#  NOTE
#   interactive tests
#
#   NOTE: requires at least version 0.15.0 of glanceclient
#   
#   $ python
#   >>> import os
#   >>> import pwd 
#   >>> import sys 
#   >>> import time
#   >>> 
#   >>> VERSION = "1"  ## NOTE !! version is 1, not 2, at leat for now !!
#   >>> USERNAME = os.environ['OS_USERNAME']
#   >>> PASSWORD = os.environ['OS_PASSWORD']
#   >>> PROJECT_ID = os.environ['OS_TENANT_NAME']
#   >>> AUTH_URL = os.environ['OS_AUTH_URL']
#   >>> 
#  
#   >>> import keystoneclient.v2_0.client as ksclient
#   >>> import glanceclient
#   
#   >>> keystone = ksclient.Client(username='jcaballero', password='xxxxxxx', tenant_name='osgsoft' , auth_url='http://cldext02.usatlas.bnl.gov:35357/v2.0/')
#   
#   >>> glance_endpoint = keystone.service_catalog.url_for(service_type='image',endpoint_type='publicURL')
#   >>> print glance_endpoint
#   http://192.153.161.7:9292
#   
#   >>> glance = glanceclient.Client(None,'http://192.153.161.7:9292/v1', token=keystone.auth_token)  # NOTE version 1 to avoid problems with missing package warlock.model
#   
#   >>> images = glance.images.list()
#   >>> print images.next()
#   {u'status': u'active', u'tags': [], u'container_format': u'bare', u'min_ram': 0, u'updated_at': u'2016-08-03T22:24:14Z', u'visibility': u'private', u'owner': u'a629decc3bc8411a83cc210326db829c', u'file': u'/v2/images/0ea3c4c9-863f    -4158-83b0-6273edd22c74/file', u'min_disk': 0, u'id': u'0ea3c4c9-863f-4158-83b0-6273edd22c74', u'size': 2075975168, u'name': u'centos7-osg-condor-execute-grid20-2016-08-03-1823', u'checksum': u'8f4ac2bdef9ea993fd66d71058b562f4', u    'created_at': u'2016-08-03T22:23:56Z', u'disk_format': u'raw', u'protected': False, u'schema': u'/v2/schemas/image'}
#   
#   >>> with open('/home/imagefactory/images/factory-build-1b47cd50-3c85-4d40-85a7-753dd0b7d5ed-iso-oz.iso') as fimage:
#   ... glance.images.create(name='fake-image-just-for-testing', is_public=False, disk_format='raw' , container_format='bare', data=fimage)
#   ...
#   
#   <Image {u'status': u'active', u'created_at': u'2016-08-26T19:43:18', u'virtual_size': None, u'name': u'fake-image-just-for-testing', u'deleted': False, u'container_format': u'bare', u'min_ram': 0, u'disk_format': u'raw', u'updated    _at': u'2016-08-26T19:43:52', u'properties': {}, u'min_disk': 0, u'protected': False, u'checksum': u'be98a34efde3455f67afbce119c7ac5d', u'owner': u'a629decc3bc8411a83cc210326db829c', u'is_public': False, u'deleted_at': None, u'id'    : u'2469326a-fcbb-4838-9293-141402d75eff', u'size': 1989038080}>
#   
#   
#    ...
#

__version__ = "0.9.1"


import commands
import os
import pwd
import sys
import time

import glanceclient
import keystoneclient.v2_0.client as ksclient


# =========================================================================

class GlanceCore:

    def __init__(self, username, password, project_id, auth_url):

        self.USERNAME = username
        self.PASSWORD = password
        self.PROJECT_ID = project_id
        self.AUTH_URL = auth_url

        keystone = ksclient.Client(username=self.USERNAME, 
                                   password=self.PASSWORD, 
                                   tenant_name=self.PROJECT_ID, 
                                   auth_url=self.AUTH_URL)
        glance_endpoint = keystone.service_catalog.url_for(service_type='image',
                                                           endpoint_type='publicURL')
        self.client = glanceclient.Client(None, 
                                          glance_endpoint+'/v1', 
                                          token=keystone.auth_token)


    def get_list_images(self):
    
        list_images = self.client.images.list() #returns a generator
        list_images = list(list_images)
        return list_images


    def get_image(self, image_name):

        try:
            return self.client.images.find(name=image_name)
        exception Exception, ex:
            raise Exception


    def create_image(self, filename, image_name):

        with open(filename) as fimage:
            self.client..images.create(name=image_name, 
                                       is_public=False, 
                                       disk_format='raw', 
                                       container_format='bare', 
                                       data=fimage)


