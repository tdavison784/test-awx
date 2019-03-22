#!/usr/bin/python

import subprocess as sp
import os
import datetime
from ansible.module_utils.basic import AnsibleModule
import xml.etree.ElementTree as ET


ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

TODO='''
Need to implement uninstallAll flag to remove all packages
'''

DOCUMENTATION='''
---

module: imcl.py
short_description: Module to install, update, and uninstall any WAS packages
description:
    - Module to install, update, and uninstall any packages for WAS
    - Can be done via response file, or package, and install dir specifications
    - If no dest is givin, a default WAS_HOME of: /opt/WebSphere/AppServer8.5.5 is given
version_added: "2.0"
author: Tommy Davison <tommy.davison@state.mn.us>
options:
    dest:
      description:
        - Type: string
        - Required: False
        - Only required when response_loc not specified
        - Or installing suppliment packages. Ie. IHS Plugins    

    package:
      description:
        - Type: string
        - Required: False
        - Only required when response_loc not specified
        - Or installing additional packages into a cell

    response_file:
      description:
        - Type: Boolean
        - Required: False
        - Only required when reponse_loc is specified

    response_loc:
        description:
          - Type: string
          - Required: False
          - Only required when installing from a response file

    state:
      description:
        - Type: string
        - Required: False
        - Only requried when response_loc is not specified
        - Choices: absent, present, update

'''

EXAMPLE='''
---
-
  name: Install WAS via Response File
  imcl:
    response_loc: /was855/InstallResponse.xml
    response_file: true

---
-
  name: Install WAS Base Package Only
  imcl:
    src: /was855/WAS_855_BASE
    state: present
    package: com.ibm.websphere.IBMJAVA.v71_7.1.1000.20140723_2109

---
-
  name: Remove single WAS Package
  imcl:
    state: absent
    package: com.ibm.websphere.IBMJAVA.v71_7.1.1000.20140723_2109
'''


def imcl_run():
    module_args = dict(
        response_loc=dict(type='str', required=False),
        response_file=dict(type='bool', required=False),
        state=dict(type='str', required=False, choices=['absent', 'present','update']),
        src=dict(required=False),
        dest=dict(required=False),
        package=dict(required=False),
        imcl_path=dict(type='str', required=True)
    )
    

    module = AnsibleModule(
        argument_spec=module_args
    )

    response_loc = module.params['response_loc']
    response_file = module.params['response_file']
    state = module.params['state']
    src = module.params['src']
    dest = module.params['dest']
    package = module.params['package']
    imcl_path = module.params['imcl_path']

    date = datetime.datetime.now()
    date_format = date.strftime("%Y%M%D%H%M")

    if response_file == True:
        rsp_file = ET.parse(response_loc)
        rsp_file_root = rsp_file.getroot()
        for inst_loc in rsp_file_root.getiterator('profile'):
            loc = inst_loc.attrib
            if os.path.exists(loc['installLocation']) == True:
                module.exit_json(
                    msg='WAS ND is already installed',
                    changed=False
                )

    if response_file == True:
        rsp_file = ET.parse(response_loc)
        rsp_file_root = rsp_file.getroot()
        for inst_loc in rsp_file_root.getiterator('profile'):
            loc = inst_loc.attrib
            if os.path.exists(loc['installLocation']) == False:
                child = sp.Popen(
                    [
                        imcl_path + ' -acceptLicense ' +
                        '-log /tmp/WAS_ND_Install-'+date_format+'.log ' +
                        '-input ' + response_loc
                    ],
                    shell=True,
                    stdout = sp.PIPE,
                    stderr = sp.PIPE
                )
                stdout_value, stderr_value = child.communicate()
                if child.returncode != 0:
                    module.fail_json(
                        msg='Failed to install WAS. For more details check log in /tmp/',
                        changed=False,
                        stderr=stderr_value,
                        stdout=stdout_value
                    )
                module.exit_json(
                    msg='Succesfully installed WAS ND.',
                    changed=True
                )

    if state == 'present' and os.path.exists(dest+'/bin/versionInfo.sh') == False:
        child = sp.Popen(
            [
                imcl_path + ' -acceptLicense ' +
                '-log /tmp/WAS_ND_Install-'+date_format+'.log ' +
                '-repositories ' + src + ' -installationDirectory ' +
                dest + ' install ' + package +
                ' -sharedResourcesDirectory /opt/WebSphere/IMShared'
            ],
            shell=True,
            stdout = sp.PIPE,
            stderr = sp.PIPE
        )
        stdout_value, stderr_value = child.communicate()
        if child.returncode != 0:
            module.fail_json(
                msg='Failed to install WAS. For more details see log in /tmp/',
                changed=False,
                stderr = stderr_value,
                stdout = stdout_value
            )
        module.exit_json(
            msg='Succesfully installed package ' + package,
            changed=True
        )
    elif state == 'present' and os.path.exists(dest+'/bin/versionInfo.sh'):
        module.exit_json(
            msg='WAS ND is already installed',
            changed=False
        )
        
    if state == 'update':
        child = sp.Popen(
            [
                imcl_path + ' listInstalledPackages'
            ],
            shell=True,
            stdout = sp.PIPE,
            stderr = sp.PIPE
        )
        stdout_value, stderr_value = child.communicate()
        packages = stdout_value.splitlines()
        if package in packages:
            module.exit_json(
                msg='Package ' + package + ' is already installed.',
                changed=False
            )
        if package not in packages:
            child = sp.Popen(
                [
                    imcl_path + ' -acceptLicense ' +
                    '-log /tmp/WAS_ND_Update-'+date_format+'.log ' +
                    '-sharedResourcesDirectory /opt/WebSphere/IMShared ' +
                    '-repositories ' + src + ' install ' + package
                ],
                shell=True,
                stdout = sp.PIPE,
                stderr = sp.PIPE
            )
            stdout_value, stderr_value = child.communicate()
            if child.returncode != 0:
                module.fail_json(
                    msg='Failed to update package ' + package + ' into cell.',
                    changed=False,
                    stderr = stderr_value,
                    stdout = stdout_value
                )
            module.exit_json(
                msg='Succesfully updated package ' + package + ' into cell',
                changed=True
            )

    if state == 'absent':
        child = sp.Popen(
            [
                imcl_path + ' listInstalledPackages'
            ],
            shell=True,
            stdout = sp.PIPE,
            stderr = sp.PIPE
        )
        stdout_value, stderr_value = child.communicate()
        packages = stdout_value.splitlines()

        if package in packages:
            child = sp.Popen(
                [
                    imcl_path + ' uninstall ' + package
                ],
                shell=True,
                stdout = sp.PIPE,
                stderr = sp.PIPE
            )
            stdout_value, stderr_value = child.communicate()
            if child.returncode != 0:
                module.fail_json(
                    msg='Failed to uninstall package ' + package + ' from cell.',
                    changed=False,
                    stderr = stderr_value,
                    stdout = stdout_value
                )
            module.exit_json(
                msg='Succesfully uninstalled package ' + package + ' from cell.',
                changed=True
            )
        if package not in packages:
            module.exit_json(
                msg='Package ' + package + ' is not installed in this cell.',
                changed=False
            )

    

def main():
    imcl_run()


if __name__ == '__main__':
    main()
