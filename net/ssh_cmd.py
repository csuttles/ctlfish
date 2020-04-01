#!/usr/bin/env python3

import os
import paramiko
import subprocess
import threading


def ssh_cmd(ip=None, port=22, username=os.environ['USER'], password=None, cmd='id'):
    """
    run a command over ssh with sensible defaults
    :param ip: ip/hostname to connect (default is effectively 'localhost')
    :param username: username to connect as, defaults to $USER from os env of process
    :param password: hunter2
    :param cmd: command to run, defaults to 'id'
    :param port: port to connect to, defaults to 22 of course
    :return:
    """
    # define client instance and set host key to autoadd - YOLO!
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # connect
    client.connect(hostname=ip, port=port, username=username, password=password)
    # get a session from our connection
    ssh_session = client.get_transport().open_session()

    if ssh_session.active:
        ssh_session.exec_command(cmd)
        print(ssh_session.recv(4096))
    return


ssh_cmd()