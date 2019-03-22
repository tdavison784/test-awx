#!/usr/bin/python

import os
from ansible.module_utils.basic import AnsibleModule


ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: ibm_imcl

short_description: Module that takes care of installing packages via imcl cli.

version_added: "2.3"

description:
    - Module that takes care of installing IBM products via imcl cli.
    - Module does a package lookup within the target cell to check for package existance.
    - Depending on the specified module state, the package check will determine the outcome of the run.
    - Module supports dry runs.

options:
    state:
        description:
            - Specified state of package.
        required: true
        choices:
          - present
          - absent
          - update
          - rollback
    src:
        description:
            - Path to IBM IM installation binaries. E.g /tmp/WASND8.5.5/
        required: false
    dest:
        description:
            - Installation Path where package will be installed. E.g /opt/IBM/WebSphere/AppServer
        required_if: state == 'present'
    path:
        description:
            - Path that leads to imcl tool for installing packages.
        required: true
    properties:
        description:
            - Additonal properties to use during product install.
            - For example, in order to install IHS you will need to use
            - use user.ihs.allowNonRootSilentInstall=true,user.ihs.httpPort=8080
        required: false
    name:
        description:
            - Name of package to be installed, updated, or removed from any given cell.
        required: true
    shared_resource:
        description:
            - Path to sharedResources directory for Product install. E.g /opt/IBM/IMShared
        required_if: state == 'present' or 'update'
    remove_all:
        description:
            - Boolean of yes and no to determine whether or not to remove all packages in the cell.
            - If yes is specified it will remove all packages
            - If no is specified it will only remove a given package.
        choices:
          - yes
          - no
        default:
          - no
    secure_storage:
        description:
            - Path to the secure storage file that contains encrypted passport advantage credentials.
            - The default path for this file location is /home/user/var/ibm/InstallationManager/secure_storage
            - This file is NOT present by default, and will need to be created.
            - More info on this can be found at https://www.ibm.com/support/knowledgecenter/en/SSDV2W_1.7.3/com.ibm.cic.commandline.doc/topics/r_tools_imcl.html
        required_if: password_file != None
        default:
          - None
    password_file:
        description:
            - Password file that contains the master password to un-encrypt the secure_storage credentials.
        required_if: secure_storage != None
        default:
          - None
author:
    - Tom Davison (@tntdavison784)
'''

EXAMPLES = '''
- name: Install IBM ND version 8.5.5
  ibm_imcl:
    state: present
    src: /tmp/WASND8.5/
    dest: /opt/IBM/WebSphere/AppServer
    path: /opt/IBM/InstallationManager/eclipse/tools/imcl
    name: com.ibm.websphere.ND.v85_8.5.5012.20170627_1018
    shared_resource: /opt/IBM/IMShared
- name: Uninstall IBM ND version 8.5.5
  ibm_imcl:
    state: absent
    path: /opt/IBM/InstallationManager/eclipse/tools/imcl
    name: com.ibm.websphere.ND.v85_8.5.5012.20170627_1018
    shared_resource: /opt/IBM/IMShared
- name: Update WAS ND to FixPack 8.5.5.13
  ibm_imcl:
    state: update
    path: /opt/IBM/InstallationManager/eclipse/tools/imcl
    name: com.ibm.websphere.ND.v85_8.5.5013.20180112_1418
- name: INSTALL IBM IHS WITH PROPERTIES
  ibm_imcl:
    state: present
    path: /opt/IBM/InstallationManager/eclipse/tools/imcl
    dest: /opt/IBM/WebSphere/HTTPServer
    name: com.ibm.websphere.IHS.v85_8.5.5000.20130514_1044
    src: /tmp/IHS-Binaries/
    properties: user.ihs.allowNonRootSilentInstall=true,user.ihs.httpPort=8080
- name: ROLLBACK LATEST FIXPACK
  ibm_imcl:
    state: rollback
    name: com.ibm.websphere.ND.v85_8.5.5013.20180112_1418
    path: /opt/IBM/InstallationManager/eclipse/tools/imcl
- name: INSTALL PACKAGES FROM REMOTE REPO
  ibm_imcl:
    state: present
    path: /opt/IBM/InstallationManager/eclipse/tools/imcl
    dest: /opt/IBM/WebSphere/AppServer
    src: http://www.ibm.com/software/repositorymanager/com.ibm.websphere.ND.v85
    name: com.ibm.websphere.ND.v85_8.5.5000.20130514_1044
    shared_resource: /opt/IBM/WebSphere/IMShared
    secure_storage: /home/user/var/ibm/InstallationManager/secure_storage
    password_file: /tmp/master
'''

RETURN = '''
update:
    description: Describes state of updating a package
    type: str
message:
    description: Successfully updated package: <package_name> into cell.
install:
    description: Describes state after installing a package
    type: str
message:
    description: Successfully installed package: <package_name> into cell.
absent:
    description: Describes state after uninstalling a package.
    type: str
message:
    description: Successfully removed package: <package_name> from cell.
'''


def install_package_local(module):
    """Function that takes care of installing new packages into the target environment."""

    if module.params['properties'] is None:
        lpackage_install_cmd = """{0} -acceptLicense -repositories {1} \
                -installationDirectory {2} -log /tmp/IBM-Install.log \
                -sharedResourcesDirectory {3} install {4}""".format(module.params['path'],
                        module.params['src'], module.params['dest'], module.params['shared_resource'],
                        module.params['name'])
        lpackage_install = module.run_command(lpackage_install_cmd, use_unsafe_shell=True)

    if module.params['properties'] is not None:
        lpackage_install_cmd = """{0} -acceptLicense -repositories {1} \
                -installationDirectory {2} -log /tmp/IBM-Install.log \
                -sharedResourcesDirectory {3} install {4} -properties {5}""".format(module.params['path'],
                        module.params['src'], module.params['dest'], module.params['shared_resource'],
                        module.params['name'], module.params['properties'])
        lpackage_install = module.run_command(lpackage_install_cmd, use_unsafe_shell=True)

    if lpackage_install[0] != 0:
        module.fail_json(
            msg="Failed to install package: {0}. Please see log in /tmp for more details.".format(module.params['name']),
            changed=False,
            stderr=lpackage_install[2]
        )

    module.exit_json(
        msg="Succesfully installed package: {0}to location: {1}. For installation details please see log in /tmp/. ".format(module.params['name'],
            module.params['dest']),
        changed=True
    )


def install_package_remote(module):
    """
    Function that will install packages
    from a remote ibm repo
    """

    if module.params['properties'] is None:
        rpackage_install_cmd = """{0}/ -repositories {1} -installationDirectory {2} \
                -log /tmp/IBM_install.log -sharedResourcesDirectory {3} \
                install {4} -secureStorageFile {5} -masterPasswordFile {6} \
                -acceptLicense""".format(module.params['path'],module.params['src'],
                        module.params['dest'],module.params['shared_resources'],
                        module.params['name'],module.params['secure_storage'],
                        module.params['passwor_file'])
        rpackage_install = module.run_command(rpackage_install_cmd, use_unsafe_shell=True)

    if module.params['properties'] is not None:
        rpackage_install_cmd = """{0}/ -repositories {1} -installationDirectory {2} \
                -log /tmp/IBM_install.log -sharedResourcesDirectory {3} \
                install {4} -secureStorageFile {5} -masterPasswordFile {6} \
                -acceptLicense -properties {7}""".format(module.params['path'],module.params['src'],
                        module.params['dest'],module.params['shared_resources'],
                        module.params['name'],module.params['secure_storage'],
                        module.params['password_file'],module.params['properties'])
        rpackage_install = module.run_command(rpackage_install_cmd, use_unsafe_shell=True)

    if rpackage_install[0] != 0:
        module.fail_json(
            msg="Failed to install package(s) {0}".format(module.params['name']),
            changed=False,
            stderr=rpackage_install[2],
            stdout=rpackage_install[1]
        )
    module.exit_json(
        msg="Successfully installed package(s) {0}".format(module.params['name']),
        changed=True
    )


def update_package_local(module):
    """Function that updates packages for target environment."""
    

    lpackage_update_cmd = """{0} -acceptLicense -sharedResourcesDirectory {1} \
install {2} -repositories {3} -log /tmp/IBM-Update.log""".format(module.params['path'],
                    module.params['shared_resource'], module.params['name'], module.params['src'])

    lpackage_update = module.run_command(lpackage_update_cmd, use_unsafe_shell=True)
    if lpackage_update[0] != 0:
        module.fail_json(
            msg="Failed to update package: {0}. Please see log in /tmp/ for more details.".format(module.params['name']),
            changed=False,
            details=lpackage_update_cmd,
            stderr=lpackage_update[2]
        )
    module.exit_json(
        msg="Succesfully updated package: {0}".format(module.params['name']),
        changed=True
    )

def update_package_remote(module):
    """Function that updates packages for target environment."""

    rpackage_update_cmd = """{0} -acceptLicense -sharedResourcesDirectory {1} \
            install {2} -repositories {3} -log /tmp/IBM-Update.log \
            -secureStorageFile {4} -masterPasswordFile {5}""".format(module.params['path'],
                    module.params['shared_resource'], module.params['name'], module.params['src'],
                    module.params['secure_storage'], module.params['password_file'])

    rpackage_update = module.run_command(rpackage_update_cmd, use_unsafe_shell=True)

    if rpackage_update[0] != 0:
        module.fail_json(
            msg="Failed to update package: {0}. Please see log in /tmp/ for more details.".format(module.params['name']),
            changed=False,
            stderr=rpackage_update[2]
        )
    module.exit_json(
        msg="Succesfully updated package: {0}".format(module.params['name']),
        changed=True
    )

def rollback_package(module):
    """Function to rollback to a previous package version."""

    rllbck_pckg_cmd = """{0} rollback {1}""".format(module.params['path'],
            module.params['name'])
    rllbck_pckg = module.run_command(rllbck_pckg_cmd, use_unsafe_shell=True)

    if rllbck_pckg[0] != 0:
        module.fail_json(
            msg="Failed to rollback package: {0} because the package was not previously installed".format(module.params['name']),
            changed=False,
            stderr=rllbck_pckg[2]
        )
    module.exit_json(
        msg="Successfully rolled back package: {0}".format(module.params['name']),
        changed=True
    )


def uninstall(module):
    """ Function that will uninstall all a package
    or if all: yes is specified will uninstall all
    packages in the given WAS cell
    """

    if (module.params['remove_all'] == 'no'):
        uninstall_cmd = """{0} uninstall {1}""".format(module.params['path'],
            module.params['name'])
        uninstall = module.run_command(uninstall_cmd, use_unsafe_shell=True)
    
        if uninstall[0] != 0:
            module.fail_json(
                msg="Failed to uninstall package {0}".format(module.params['name']),
                changed=False,
                stderr=uninstall[2]
            )
        module.exit_json(
                msg="Succesfully uninstalled package {0}".format(module.params['name']),
                changed=True
        )

    if (module.params['remove_all'] == 'yes'):
        uninstallAll_cmd = """{0} uninstallAll""".format(module.params['path'])

        uninstallAll = module.run_command(uninstallAll_cmd, use_unsafe_shell=True)

        if uninstallAll[0] != 0:
            module.fail_json(
                msg="Failed to uninstall all products. See stderr/stdout for details...",
                changed=False,
                stderr=uninstallAll[2],
                stdout=uninstallAll[1]
            )

        module.exit_json(
            msg="Succesfully removed all packages",
            changed=True
        )


def package_check(module):
    """Function that will be checking target cell for package existance.
    This portion will be doing package lookups to ensure that the package being installed
    either exists in the cell, or doesn't for all module.params['state']
    """

    check_package_cmd = """{0} listInstalledPackages""".format(module.params['path'])
    check_package = module.run_command(check_package_cmd, use_unsafe_shell=True)

    name = module.params['name']

    name = name.split()
    for package in name:
      if package in check_package[1]:
          return 1
      else:
          return 0


def main():
    """Function that does all the main logic for the module.
    This portion will be doing package lookups to ensure that the package being installed
    either exists in the cell, or doesn't for all module.params['state']
    """

    module = AnsibleModule(
        argument_spec=dict(
            remove_all=dict(type='str', required=False, choices=['yes', 'no'], default='no'),
            state=dict(type='str', required=True, choices=['present', 'absent', 'update', 'rollback']),
            src=dict(type='str', required=False),
            dest=dict(type='str', required=False),
            path=dict(type='str', required=True),
            name=dict(type='str', required=False),
            shared_resource=dict(type='str', required=False),
            secure_storage=dict(type='str', required=False, default=None),
            password_file=dict(type='str', required=False, default=None),
            properties=dict(type='str', required=False, default=None)
        ),
        supports_check_mode = True,
        required_if=[
            ["state","present", ["dest", "shared_resource"],
            ["state","update", ["dest", "shared_resource"],
            [["secure_storage", "!None", ["password_file"]]]]]]
    )

    remove_all = module.params['remove_all']
    state = module.params['state']
    src = module.params['src']
    dest = module.params['dest']
    path = module.params['path']
    name = module.params['name']
    shared_resource = module.params['shared_resource']
    secure_storage = module.params['secure_storage']
    password_file =  module.params['password_file']
    properties = module.params['properties']

    if remove_all == 'yes':
        uninstall(module)

    pckg_check = package_check(module)


    if pckg_check != 1:
        if (state == 'present') and not (module.check_mode):
            install_package_local(module)
        if (state == 'present') and (secure_storage is not None) and not (module.check_mode):
            install_package_remote(module)
        if (state == 'update') and (secure_storage is None) and not (module.check_mode):
            update_package_local(module)
        if (state == 'update') and (secure_storage is not None) and not (module.check_mode):
            update_package_remote(module)
        if (state == 'rollback') and not (module.check_mode):
            rollback_package(module)
        if module.check_mode:
            if state == 'present':
                module.exit_json(msg="Package: {0} will be installed to location {1}".format(name,dest),change=True)
            if state == 'update':
                module.exit_json(msg="Package: {0} will be updated".format(name),changed=True)
            if state == 'absent':
                module.exit_json(msg="Package: {0} is not present in cell. Nothing to remove.".format(name),changed=False)
            if (state == 'rollback'):
                module.exit_json(msg="Package {0} is not present to rollback".format(name),changed=False)
    elif pckg_check != 0:
        if (state == 'present'):
            module.exit_json(msg="Package {0} is already present.".format(name),changed=False)
        if (state == 'absent') and not (module.check_mode):
            uninstall_package(module)
        if (state == 'update') and not (module.check_mode):
            module.exit_json(msg="Package {0} is already present.".format(name),changed=False)
        if (state == 'rollback') and not (module.check_mode):
            module.exit_json(msg="Package {0} not is not present to rollback.".format(name), changed=False)
        if module.check_mode:
            if (state == 'absent'):
                module.exit_json(msg="Package {0} will be removed.".format(name),changed=True)
            if (state == 'rollback'):
                module.exit_json(msg="Package {0} will be rolled back".format(name),changed=True)


if __name__ == '__main__':
    main()
