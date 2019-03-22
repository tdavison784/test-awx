#!/usr/bin/python
import subprocess as sp
from ansible.module_utils.basic import AnsibleModule
from lxml import etree

def get_versionInfo():

    module = AnsibleModule(
        argument_spec=dict(
            was_root=dict(type='str', required=True),
            product=dict(type='str', required=True, choices=['IHS', 'WAS', 'BPM'])
        )
    )

    was_root = module.params['was_root']
    product = module.params['product']

    if was_root:
        try:
            properties = etree.parse(was_root+'/properties/version/'+product+'.product')
            version = properties.find('version')
        except IOError:
            module.fail_json(
                msg=was_root+'/properties/version/'+product+'.product does not exist. This may mean that '+ product + ' is not installed'
            )
    module.exit_json(
        msg='Current version of '+ product + ' is: '+ version.text
    )


def main():
    get_versionInfo()

if __name__ == '__main__':
    main()
