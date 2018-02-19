import multiprocessing

from fabric.api import cd, lcd, run, env, reboot, execute, local, hide, settings
from time import sleep

PASSWORD = '123456'
USER = 'root'
env.user = USER
env.password = PASSWORD
env.shell = "/bin/zsh -l -c"

def run_and_report(run_commnad):
    output = run(run_commnad)
    return [output, output.stdout, output.real_command]

def run_and_report_with_cd(run_commnad, with_cd):
    with cd(with_cd):
        output = run(run_commnad)
    return [output, output.stdout, output.real_command]

def run_execute(run_command, host=False, with_cd=False):
    if host:
        if with_cd:
            output = execute(run_and_report_with_cd, run_command, with_cd, hosts=[host])
        else:
            output = execute(run_and_report, run_command, hosts=[host])
        result = output[host]
        return result[0]
    else:
        if with_cd:
            with lcd(with_cd):
                output = local(run_command, capture=True)
        else:
            output = local(run_command, capture=True)
        return output

def run_command(run_command, host=False, with_cd=False, warn_only=False, hide_output=False):
    if hide_output:
        with settings(hide('warnings', 'running', 'stdout', 'stderr'), warn_only=warn_only):
            return run_execute(run_command, host, with_cd)
    else:
        with settings(warn_only=warn_only):
            return run_execute(run_command, host, with_cd)

def copy_image_to_host(cp_from_host, cp_to_host, path_to_image, queue=False):
    ssh_permission = 'sshpass -p "{}" ssh-copy-id -o StrictHostKeyChecking=no {}@'.format(PASSWORD, USER)+cp_to_host

    if not cp_from_host or cp_from_host=='localhost':
        command = "scp {} {}@{}:~/".format(path_to_image, USER, cp_to_host)
        run_command(ssh_permission, host=False, hide_output=True)
        run_command(command, host=False, hide_output=True)
    else:
        command = "scp {0}@{1}:~/{2} {3}@{4}:~/".format(USER, cp_from_host ,path_to_image.split('/')[-1], USER, cp_to_host)
        run_command(ssh_permission, host=cp_from_host, hide_output=True)
        run_command(command, host=cp_from_host, hide_output=True)
    if queue:
        queue.put((cp_from_host, cp_to_host))
    print('finished copying from {} to {} file {}'.format(cp_from_host, cp_to_host, path_to_image))

def copy_manager(file_path, hosts):
    print('copying file {} to hosts: {}'.format(file_path, hosts))
    hosts_with_files = ['localhost']
    len_of_hosts     = len(hosts)
    copy_from        = False
    copy_to          = False
    queue            = multiprocessing.Queue()

    while True:
        try:
            print('try to get hosts')
            # getting the copy_from and copy_to
            returned_hosts = queue.get(timeout=0.2)
            print(' got back: {}'.format(returned_hosts))
        except  Exception as e:
            returned_hosts = False
            print('no hosts back from combat')
        if returned_hosts:
            print('before: {}'.format(hosts_with_files))
            # list it, as returned_hosts is a tuple
            hosts_with_files = hosts_with_files + list(returned_hosts)
            print('after: {}'.format(hosts_with_files))
        try:
            # we might still have copy_to from previous cycle so we need to check
            # if its False we wont pop again losing the one we already hold
            print("try get copy_to: {} from {}".format(copy_to, hosts))
            if not copy_to:
                copy_to = hosts.pop()
        except:
            print('except, no more to copy to: {}'.format(hosts))
            copy_to = False
            print('no more hosts to copy to? {}'.format(hosts_with_files))
            # +1 for localhost
            if (len_of_hosts+1)==len(hosts_with_files):
                print('checking if the files exist on all hosts')
                return True
        # no need to find copy from if we don't have somewhere to copy to
        # as we might get stuck with a copy_from, when hosts will be empty (all files transferred)
        if copy_to:
            try:
                # we might still have copy_from from previous cycle so we need to check
                # if its False we wont pop again losing the one we already hold
                print("try get copy_from: {} from {}".format(copy_from, hosts_with_files))
                if not copy_from:
                    copy_from = hosts_with_files.pop()
            except:
                copy_from = False

        if copy_from and copy_to:
            print('start process for {} {}'.format(copy_from, copy_to))
            p = multiprocessing.Process(target=copy_image_to_host, name='copy_file_to_host', args=(copy_from, copy_to, file_path, queue,   ))
            p.start()
            copy_to = False
            copy_from = False
        sleep(1)