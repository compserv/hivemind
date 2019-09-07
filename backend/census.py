"""census.py - SSH into servers, grab vital stats, then print to stdout."""

import json
import logging
import multiprocessing.dummy
import time

import paramiko

import os

DIR = os.path.dirname(os.path.realpath(__file__))
SERVER_LIST = os.path.join(DIR, 'servers.txt')
HOST_SUFFIX = '.berkeley.edu'
LOGIN_USERNAME = 'hivemind'
LOGIN_KEY_PATH = os.path.expanduser('~') + '/.ssh/hivemind_rsa'

LOG_PATH = os.path.join(os.path.dirname(DIR), 'log', 'output.log')
LOG_LEVEL = logging.INFO

EXEC_CMD = 'cat /proc/{uptime,loadavg} && who -q && getconf _NPROCESSORS_ONLN'
EXPECTED_OUTPUT_LINES = 5

THREAD_COUNT = 20


def read_servers(list_path=SERVER_LIST):
    """Returns list of servers to look at.
    Reads SERVER_LIST by default.
    """
    with open(list_path, 'r') as list:
        return [server.strip() for server in list.readlines()]


def poll(host):
    """Collects data from the given server by SSH-ing in (using pysftp) and
    running the EXEC_CMD. Returns a tuple: the first member is the output as
    a list of strings; the second is the elapsed time in seconds.
    """
    t_start = time.time()
    logging.info('Starting poll of %s' % host)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    privkey = paramiko.RSAKey.from_private_key_file(LOGIN_KEY_PATH)
    ssh.connect(
        hostname=host + HOST_SUFFIX,
        username=LOGIN_USERNAME,
        pkey=privkey,
        timeout=10,
        banner_timeout=5,
        auth_timeout=5,
    )

    stdin, stdout, stderr = ssh.exec_command(EXEC_CMD)
    result = stdout.readlines()

    if len(result) != EXPECTED_OUTPUT_LINES:
        raise ValueError('Server output has wrong number of lines: %r'
                         % result)

    result = [s.rstrip('\n') for s in result]

    uptime = float(result[0].split(' ')[0])  # in seconds
    num_cpus = float(result[4])
    loadavgs = [float(avg) / num_cpus for avg in result[1].split(' ')[:3]]  # over last 15 minutes
    users = [] if not result[2] else list(set(result[2].split(' ')))
    data = {
        'uptime': uptime,
        'load_avgs': loadavgs,
        'users': users,
    }

    t_elapsed = time.time() - t_start
    logging.info('Finished poll of %s successfully in %fs' % (host, t_elapsed))
    return data, t_elapsed

if __name__ == '__main__':
    """Reads list of servers, then grabs data from each one. Prints the combined
    data in JSON format to stdout and writes a log to LOG_PATH."""
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        filename=LOG_PATH,
        level=LOG_LEVEL,
    )
    results = {'time_begin': time.time(), 'data': {}}

    def task(server):
        try:
            return server, poll(server)
        except:
            return server, None

    def callback(callback_results):
        for server, result in callback_results:
            if result != None:
                server_data, server_elapsed = result
                results['data'][server] = server_data
            else:
                results['data'][server] = {}

    servers = read_servers()
    pool = multiprocessing.dummy.Pool(THREAD_COUNT)

    pool.map_async(task, servers, callback=callback)
    pool.close()
    pool.join()

    results['time_elapsed'] = time.time() - results['time_begin']
    logging.info('===== Finished in %fs' % results['time_elapsed'])
    print(json.dumps(results, sort_keys=True))
