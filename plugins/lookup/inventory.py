# python 3 headers, required if submitting to Ansible
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = """
  lookup: inventory
  author: Dougal Seeley (github@dougalseeley.com)
  short_description: Load an inventory plugin as a lookup
  description:
    - This lookup returns the inventory as an array of [{groups:[hosts:vars]}]
  options:
    _terms:
      description: inventory plugin (i.e. one from 'ansible-doc -t lookup -l')
      required: True
    plugin_options:
      description: Key-value options that would normally be defined in the inventory plugin yml file
      type: dict
      default: {}
"""

EXAMPLES = """
- name: Get vmware inventory info
  debug:
    msg: "{{ lookup('dseeley.inventory_lookup.inventory', 'community.vmware.vmware_vm_inventory', plugin_options=params) }}"
  vars:
    params:
      hostname: "{{ esxi_ip }}"
      username: "{{ esxi_username }}"
      password: "{{ esxi_password }}"
      validate_certs: false
      hostnames: ['config.name']
      keyed_groups: []

- name: Get community.libvirt inventory info
  debug:
    msg: "{{ lookup('dseeley.inventory_lookup.inventory', 'community.libvirt.libvirt', plugin_options=params) }}"
  vars:
    params:
      uri: 'qemu+ssh://{{ username }}@{{ libvirt_ip }}/system?keyfile=id_rsa'

- name: Get aws inventory info (Note - aws_ec2 inventory plugin returns datetime.datetime objects, so this doesn't parse as json)
  debug:
    msg: "{{ lookup('dseeley.inventory_lookup.inventory', 'amazon.aws.aws_ec2', plugin_options=params) }}"
  vars:
    params:
      aws_access_key: "{{ aws_access_key }}"
      aws_secret_key: "{{ aws_secret_key }}"
      region: "{{ region }}"
      validate_certs: false
      keyed_groups: []

- name: Get proxmox inventory info
  debug:
    msg: "{{ lookup('dseeley.inventory_lookup.inventory', 'community.general.proxmox', plugin_options=params) }}"
  vars:
    params:
      url: "https://192.168.1.70:8006"
      user: root@pam
      password: 'PASSWD'
      validate_certs: false
      want_facts: true
"""

from ansible.errors import AnsibleOptionsError
from ansible.inventory.data import InventoryData
from ansible.module_utils.common._collections_compat import Mapping
from ansible.module_utils.six import string_types
from ansible.parsing.dataloader import DataLoader
from ansible.plugins.loader import inventory_loader
from ansible.plugins.lookup import LookupBase
from ansible.utils.display import Display

display = Display()


class LookupModule(LookupBase):
    def run(self, terms, variables=None, **kwargs):
        display.vvv("inventory_plugin / terms: %s" % terms)

        if len(terms) > 1:
            raise AnsibleOptionsError("This plugin only supports a single term: %s" % terms)

        # Support both string and dict types for plugin options
        if isinstance(terms[0], Mapping):
            self.set_options(var_options=variables, direct=terms[0])
        elif isinstance(terms[0], string_types):
            self.set_options(var_options=variables, direct=kwargs)

        display.vvv("inventory_plugin / options: %s" % self.get_options())

        inventory = InventoryData()

        # Load the inventory plugin
        plugin = inventory_loader.get(terms[0])

        # Redefine the _read_config_data() function to do nothing (prevent the plugin looking for (and erroring on failing to find) the non-existent config file)
        plugin._read_config_data = lambda *args: {}

        for option in self.get_option('plugin_options').items():
            plugin.set_option(option[0], option[1])

        # Do the actual inventory parsing
        plugin.parse(inventory, DataLoader(), '/dev/null')

        # Ensure inventory basic rules
        inventory.reconcile_inventory()

        display.vvv("inventory_plugin / get_groups_dict: %s" % plugin.inventory.get_groups_dict())

        # lookups in general are expected to both take a list as input and output a list
        # this is done so they work with the looping construct 'with_'.
        ret = []
        for (group_name, group) in plugin.inventory.groups.items():
            ret.append({group_name: [{h.name: h.get_vars()} for h in group.get_hosts()]})

        return ret
