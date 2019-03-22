#!/usr/bin/python

import os
from ansible.module_utils.basic import AnsibleModule

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: ibm_im

short_description: Module that takes care of installing IBM Installation Manager IBM IM

version_added: "2.1"

description:
    - Module that takes care of installing IBM IM.
    - IBM IM is the first needed install for most IBM Middleware products.
    - These products include but are not limited to, IBM WAS, IBM BPM, IBM RTC

options:
    state:
        description:
            - Specified state of IBM IM. Present will install, and absent will uninstall.
        required: true
        choices:
          - present
          - absent
    src:
        description:
            - Path to IBM IM installation binaries. E.g /tmp/IM.1.8/
        required: true
    dest:
        description:
            - Installation Path where IBM IM will be installed. E.g /opt/IBM/InstallationManager/
        required: false


author:
    - Tom Davison (@tntdavison784)
'''

EXAMPLES = '''
- name: Install IBM IM with non standard dest
  ibm_im:
    state: present
    src: /was855/IM.1.8/
    dest: /opt/IBM/InstallationManager
- name: Install IBM IM with standard dest
  ibm_im:
    state: present
    src: /was855/IM.1.8/
- name: Remove IBM IM
  ibm_im:
    state: absent
    src: /home/user/var/ibm/InstallationManager
'''


RETURN = '''
result:
    description: Descibes changed state or failed state
    type: str
message:
    description: Succesfully installed or uninstalled IBM IM

'''

def install_ibmim(module, src, dest):
    """Function that will install IBM Installation Manager.
    This will only get installed if an installation path with a binary related to the install
    is not located on the server. If the binary is found, install will skip.
    """

    if os.path.exists(dest+"/eclipse/tools/imcl"):
        module.exit_json(
            msg="Installation Manager already exists at %s" % (dest),
            changed=False
        )
    else:
        install_im = module.run_command(src+'/userinstc -acceptLicense -installationDirectory ' +
                                        dest, use_unsafe_shell=True)

        if install_im[0] != 0:
            module.fail_json(
                msg="Failed to install IBM IM at %s" % (dest),
                changed=False,
                stderr=install_im[2]
            )
        else:
            module.exit_json(
                msg="Succesfully installed IBM IM at %s" % (dest),
                changed=True,
            )

def remove_ibmim(module, src):
    """Function that will remove IBM IM installation.
    The removal of IBM IM is associated with the installation users home directory.
    The uninstall binaries are located on RHEL/centos: /home/user/var/ibm/InstallationManager/uninstall/ directory.
    """


    try:
        if os.path.exists(src):
            uninstall_im = module.run_command(src+'/uninstallc', use_unsafe_shell=True)
            if uninstall_im[0] != 0:
                module.fail_json(
                    msg="Failed to uninstall IBM IM.",
                    changed=False,
                    stdout=uninstall_im[1],
                    stderr=uninstall_im[2]
                )
            module.exit_json(
                msg="Succesfully uninstalled IBM IM",
                changed=True
             )

        else:
            module.fail_json(
                msg="The src directory of %s does not appear to exist." % (src),
                changed=False
            )
    finally:
        pass

def main():
    """Function that will do all the main logic for the module."""

    module = AnsibleModule(
        argument_spec=dict(
            state=dict(required=True, type='str', choices=['present', 'absent']),
            src=dict(required=True, type='str'),
            dest=dict(required=False, type='str')
        ),
        supports_check_mode=True
    )

    state = module.params['state']
    src = module.params['src']
    dest = module.params['dest']

    if state == 'present' and not module.check_mode:
        install_ibmim(module, src, dest)

    if state == 'absent' and not module.check_mode:
        remove_ibmim(module, src)

    if module.check_mode:
        if state == 'present':
            if os.path.exists(dest+"/eclipse/tools/imcl"):
                module.exit_json(
                    msg="IBM IM is already installed at location %s." % (dest),
                    changed=False
                )
            else:
                module.exit_json(
                    msg="Sucessfully installed IBM IM at location %s." % (dest),
                    changed=True
                )
        if state == 'absent' and not os.path.exists(src+"/uninstallc"):
            module.exit_json(
                msg="IBM IM is not present.",
                changed=False
            )
        else:
            module.exit_json(
                msg="Succesfully uninstalled IBM IM.",
                changed=True
            )

if __name__ == '__main__':
    main()
