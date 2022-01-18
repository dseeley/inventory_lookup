# Ansible Collection - dseeley.inventory_lookup

An Ansible plugin to load an inventory plugin as a lookup

## Execution
This is run as an Ansible lookup:
```yaml
- debug:
    msg: "{{ lookup('inventory_plugin', 'community.vmware.vmware_vm_inventory', plugin_options=params) }}"
  vars:
    params:
      hostname: '192.168.1.3'
      username: 'svc'
      password: 'ESXI_PASSWD'
      validate_certs: False
      hostnames: ['config.name']
      keyed_groups: []
```
`