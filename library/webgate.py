#!/usr/bin/python


import os
import subprocess as sp
from ansible.module_utils.basic import AnsibleModule
import time


def set_params():
    """Function to set all needed params for Ansible Usage
    This function will need to be called in main function first to init
    all needed args in order to run
    """
    global module 
    global ora_inst
    global response_loc

    module_args=dict(
        ora_inst=dict(type='str', required=True),
        response_loc=dict(type='str', required=True)
    )

    module=AnsibleModule(
        argument_spec=module_args
    )

    ora_inst = module.params['ora_inst']
    response_loc = module.params['response_loc']

    
def check_for_ofm():
    """Function to check for Oracle 11g webgate installation
    if os.path.exits():
        return True
    else:
        return False
    """


    ofm_install_dir='/opt/OAM/oracle'

    if os.path.exists(ofm_install_dir):
        return True
    else:
        return False

def check_for_webgate():
    """Function to check for webgate httpd.conf.ORIG precense
    if os.path.exits(http_conf_ORIG):
        return True
    else:
        return False
    """

    http_conf_ORIG='/opt/WebSphere/HTTPServer/conf/httpd.conf.ORIG'

    if not os.path.exists(http_conf_ORIG):
        return False
    else:
        return True


def check_for_java():
    """Function to check for java on OS"""

    os_java='/usr/bin/java'

    if os.path.exists(os_java):
        return True
    else:
        return False


def install_webgate():
    """Function to install webgate"""

    t = sp.Popen(
        [
            '/was855/OAM-11g/Disk1/runInstaller -silent -response ' +
            response_loc + ' -jreLoc /usr/ -invPtrLoc ' + ora_inst +
            ' -ignoreSysPrereqs'
        ],
        shell=True,
        stdout=sp.PIPE,
        stderr=sp.PIPE
    )
    stdout_value, stderr_value = t.communicate()

    if t.returncode != 0:
        return False
    else:
        return True


def create_webgate():
    """Function to create Webgate instance
    After ofm install completed
    """
    global t1
    t1 = sp.Popen(
        [
            '/opt/OAM/oracle/product/11.1.1/as_1/webgate/ihs/tools/deployWebGate/deployWebGateInstance.sh -w ' +
            '/opt/OAM/oracle/Middleware/Oracle_OAMWebGate1 -oh /opt/OAM/oracle/product/11.1.1/as_1/ -ws ihs'
        ],
        shell=True,
        stdout=sp.PIPE,
        stderr=sp.PIPE
    )
    stdout_value, stderr_value = t1.communicate()

    if t1.returncode != 0:
        return False
    else:
        return True


def edit_httpdConf():
    """Function to edit IHS httpd.conf file
    To insert 11g apache modules
    """
    t2 = sp.Popen(
        [
            '/opt/OAM/oracle/product/11.1.1/as_1/webgate/ihs/tools/setup/InstallTools/EditHttpConf -f /opt/WebSphere/HTTPServer/conf/httpd.conf -w /opt/OAM/oracle/Middleware/Oracle_OAMWebGate1 -oh /opt/OAM/oracle/product/11.1.1/as_1/ -ws ihs'
        ],
        shell=True,
        stdout=sp.PIPE,
        stderr=sp.PIPE
    )
    stdout_value, stderr_value = t2.communicate()



def main():
    """Function to put all the peices together"""
    set_params()

    if check_for_java() == False:
        module.fail_json(
            msg='Failed. No Java was found on the system. Please install JAVA to continue.',
            changed=False
        )

    if check_for_ofm():
        module.exit_json(
            msg='Oracle WebGate is already installed on the server',
            changed=False
        )

    if install_webgate():
        if create_webgate():
            module.exit_json(msg='Succesfully created IHS Oracle Webgate instance',changed=True)
        else:
            module.fail_json(msg='Failed to create Webgate instance',changed=False)
    else:
        module.fail_json(msg='Failed to install Oracle WebGate',changed=False)


if __name__ == '__main__':
    main()
