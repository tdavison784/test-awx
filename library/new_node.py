#!/usr/bin/python

import os
from ansible.module_utils.basic import AnsibleModule

def main():
    """Main function to process the logic. Will load in the other functions
    and process the input. Changed state varies depending on the input from
    the other functions.
    """


    module_args=dict(
        profile=dict(type='str', required=True),
        state=dict(type='str', required=True, choices=['stop', 'start', 'restart']),
        path=dict(type='str', required=True)
    )

    module = AnsibleModule(
        argument_spec=module_args
    )

    profile = module.params['profile']
    state = module.params['state']
    path = module.params['path']


    def pid_exists(path, profile):
        """Function to check for .pid file existance
        This is needed for ansible to be idempontent when start/stop service
        Function will stat path, profile logs nodeagent dir
        and check for nodeagent.pid file.
        if pid:
            return 1
        else:
            return 0
        """
    

        existance = os.path.exists(path+'/profiles/'+profile+'/logs/nodeagent/nodeagent.pid')

        if existance:
            return 1
        else:
            return 0




    if pid_exists(path, profile) == 1:

        def read_pid(path, profile):
            """Function that depends on the return value of _pid_exists function.
            If the _pid_exists function returns 1, read_pid will open the .pid
            file and read in the pid value to check system for a running value.
            This is needed to due a kill -9 <pid#1>. If a pid is closed unexpectedly
            it will leave the .pid file in existance, so we need to check and ensure
            that the pid isn't running.
            """

            pid_file = path+'/profiles/'+profile+'/logs/nodeagent/nodeagent.pid'

            with open(pid_file, 'r') as f_obj:
                pid_num = f_obj.readline()
                f_obj.close()

                return int(pid_num)

        def pid_running():
            """Function that will check system processes for pid number
            that is returned from read_pid function if _pid_exists returns 1
            value. We will use os.kill(0, pid) method. Sending signal 0 to a pid
            will raise on OSError exception if pid is not running, and do nothing otherwise.
            if the pid is running:
               return 1
            else:
              return 0
            """

            try:
                os.kill(read_pid(path, profile), 0)
            except OSError:
                return 0
            else:
                return 1




        if state == 'start'  and pid_running() != 0:
            module.exit_json(
                msg='Node agent is already in a %s state for profile %s ' % (state, profile),
                changed=False
            )
        elif state == 'start':
            start = module.run_command(path + '/profiles/' + profile + '/bin/startNode.sh',use_unsafe_shell=True)
            if start[0] != 0:
                module.fail_json(
                    msg='Failed to %s node agent for profile %s ' % (state, profile),
                    changed=False,
                    stdout=start[1],
                    stderr=start[2] #This may also be 1, we shall see
                )
            module.exit_json(
                msg='Succesfully sent node agent into a %s state for profile %s' % (state, profile),
                changed=True
            )


        if state == 'stop' and pid_running() != 1:
           module.exit_json(
                msg='Node agent is already in a %s state for profile %s' % (state, profile),
                changed=False
            )
        elif state == 'stop':
            stop = module.run_command(path + '/profiles/' + profile + '/bin/stopNode.sh',use_unsafe_shell=True)
            if stop[0] != 0:
                module.fail_json(
                    msg='Failed to %s node agent for profile %s ' % (state, profile),
                    changed=False,
                    stdout=start[1],
                    stderr=start[2] #This may also be 1, we shall see
                )
            module.exit_json(
                msg='Succesfully sent node agent into a %s state for profile %s' % (state, profile),
                changed=True
            )

if __name__ == '__main__':
    main()

