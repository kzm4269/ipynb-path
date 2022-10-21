import functools as ft
import itertools as it
import os
import re

import requests


def list_running_servers():
    try:
        from notebook.notebookapp import list_running_servers
        for server in list_running_servers():
            yield server
    except ImportError:
        pass

    try:
        from jupyter_server.serverapp import list_running_servers
        for server in list_running_servers():
            yield server
    except ImportError:
        pass


class JupyterRestfulApi(requests.Session):
    def __init__(self, server, passwords=None):
        super(JupyterRestfulApi, self).__init__()
        self.server = dict(server)

    @ft.wraps(requests.Session.request)
    def request(self, method, url, *args, **kwargs):
        return super(JupyterRestfulApi, self).request(
            method,
            requests.compat.urljoin(self.server['url'], url),
            *args,
            **kwargs,
        )

    def login(self, password=None):
        if not self.server['token'] and not self.server['password']:
            pass
        elif self.server['token']:
            self.headers['Authorization'] = 'token ' + self.server['token']
        elif self.server['password']:
            self.get('')
            self.post(
                'login?next=%2Flab',
                data={
                    'password': password,
                    '_xsrf': self.cookies['_xsrf'],
                },
            )
        else:
            assert False

        response = self.get('api/sessions')
        response.raise_for_status()
        if 'message' in response.json():
            raise requests.RequestException(response)

    @classmethod
    def login_all(cls, password=None, strict=False):
        if isinstance(password, (str, bytes)):
            passwords = [password]
        else:
            try:
                passwords = list(password)
            except TypeError:
                passwords = [password]

        for client in map(cls, list_running_servers()):
            for trust_env, password in it.product(
                [False, True],
                [None] + passwords,
            ):
                try:
                    client.trust_env = trust_env
                    client.login(password)
                except (requests.HTTPError, requests.RequestException):
                    if strict:
                        raise
                else:
                    yield client
                    break


def current_kernel_id():
    try:
        from ipykernel.connect import get_connection_file

        return re.search(
            r'kernel-([\w-]+)\.json$',
            get_connection_file(),
        ).group(1)
    except ImportError:
        return None

def find_current_session(clients):
    kid = current_kernel_id()
    for client in clients:
        for session in client.get('api/sessions').json():
            if session['kernel']['id'] == kid:
                return client, session
    raise ValueError('Could not find the current session.')


def current_notebook_path(password=None):
    clients = JupyterRestfulApi.login_all(password=password)
    client, session = find_current_session(clients)
    root_dir = client.server.get('notebook_dir')
    if root_dir is None:
        root_dir = client.server['root_dir']
    return os.path.join(root_dir, session['path'])
