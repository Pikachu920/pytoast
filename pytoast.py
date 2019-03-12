import win32con
import win32gui
import pkg_resources
from uuid import uuid4
from os import path


def __close_window(window_handle, window_class):
    """
    Unregisters and destroys a window
    """
    # https://archive.is/BWQv6
    win32gui.DestroyWindow(window_handle)
    # https://archive.is/53x2A
    win32gui.UnregisterClass(window_class.lpszClassName, None)


def show_toast(title, body, **kwargs):
    """
    Displays a toast notification

    :param title: The title of the toast
    :param body: The body of the toast
    :param kwargs: See below
    """

    # https://archive.is/j8iU1
    window_class = win32gui.WNDCLASS()
    window_class.lpszClassName = kwargs.get('window_class', f'PythonToast-{uuid4().hex}')

    # http://archive.is/OuczF, http://archive.is/t4bdM
    # noinspection PyUnusedLocal
    def on_destroy(hwnd, msg, wparam, lparam):
        # https://archive.is/jRGRC, https://archive.is/wv6Nz
        win32gui.Shell_NotifyIcon(
            win32gui.NIM_DELETE,
            (
                test,
                0
            )
        )
        # https://archive.is/g0jSW
        win32gui.PostQuitMessage(0)

    window_class.lpfnWndProc = {
        win32con.WM_DESTROY: on_destroy
    }

    handle = win32gui.GetModuleHandle(None)

    try:
        class_atom = win32gui.RegisterClass(window_class)
    except Exception as e:
        raise Exception('Window registration failed', e)

    # https://archive.is/bnUYr
    window_handle = win32gui.CreateWindow(
        class_atom,
        kwargs.get('window_title', 'Toast'),
        win32con.WS_OVERLAPPED | win32con.WS_SYSMENU,  # style
        0,  # x coord
        0,  # y coord
        win32con.CW_USEDEFAULT,  # width
        win32con.CW_USEDEFAULT,  # height
        0,  # parent window (0 = none)
        0,  # menu (0 = none)
        handle,
        None  # additional app data (we have none)
    )
    test = window_handle

    win32gui.UpdateWindow(window_handle)

    try:
        icon_path = path.realpath(path.expanduser(kwargs['icon']))
    except KeyError:
        icon_path = pkg_resources.resource_filename('pytoast', 'data/default_icon.ico')

    # https://archive.is/hDS2B
    try:
        icon_handle = win32gui.LoadImage(
            handle,
            icon_path,
            win32gui.IMAGE_ICON,
            0,  # width, 0 = actual width
            0,  # height, 0 = actual height
            win32gui.LR_LOADFROMFILE | win32gui.LR_DEFAULTSIZE
        )
    except Exception as e:
        __close_window(window_handle, window_class)
        raise ValueError(f'Invalid icon path: {icon_path}', e)

    # https://archive.is/jRGRC, https://archive.is/wv6Nz
    win32gui.Shell_NotifyIcon(
        win32gui.NIM_ADD,
        (
            window_handle,
            0,
            win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP,
            win32con.WM_USER + 20,
            icon_handle,
            kwargs.get('tooltip', 'Toaster')
        )
    )

    # https://archive.is/jRGRC, https://archive.is/wv6Nz
    win32gui.Shell_NotifyIcon(
        win32gui.NIM_MODIFY,
        (
            window_handle,
            0,
            win32gui.NIF_INFO,
            win32con.WM_USER + 20,
            icon_handle,
            kwargs.get('balloon_tooltip', kwargs.get('tooltip', 'Toaster')),
            body,
            200,
            title
        )
    )

