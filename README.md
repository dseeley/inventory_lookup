# Ansible Collection - dseeley.inventory_lookup

An Ansible plugin to load an inventory plugin as a lookup

## Execution
This is run as an Ansible lookup:
```yaml
- name: Get vmware inventory info
  debug:
    msg: "{{ lookup('dseeley.inventory_lookup.inventory', 'community.vmware.vmware_vm_inventory', plugin_options=params) }}"
  vars:
    params:
      hostname: "{{ esxi_ip }}"
      username: "{{ esxi_username }}"
      password: "{{ esxi_password }}"
      validate_certs: False
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
      validate_certs: False
      keyed_groups: []

- name: Get proxmox inventory info
  debug:
    msg: "{{ lookup('dseeley.inventory_lookup.inventory', 'community.general.proxmox', plugin_options=params) }}"
  vars:
    params:
      url: "https://192.168.1.70:8006"
      user: root@pam
      password: 'PASSWD'
      validate_certs: False
      want_facts: yes
```
