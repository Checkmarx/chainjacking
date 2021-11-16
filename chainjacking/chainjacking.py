import logging
import os
import re
import shutil
import subprocess
import tempfile
import time

import requests

logger = logging.getLogger(__name__)


def _is_github_username_exists(username, github_token, rate_limit_sleep_seconds=20, max_rate_limit_attempts=5):
    headers = {'Authorization': f'token {github_token}'}
    attempt = 0
    while True:
        if attempt > max_rate_limit_attempts:
            raise Exception(f'Retried {max_rate_limit_attempts} times, Exiting. Try increasing the number of attempts allowed')

        attempt += 1

        r = requests.head(f'https://api.github.com/users/{username}', headers=headers, allow_redirects=False)
        if r.status_code == 404:
            return False
        if r.status_code == 401:
            logger.error('Your GitHub token is invalid')
            raise Exception(f'Your GitHub token is invalid')
        elif r.status_code == 403:
            logger.debug(f"Reached GitHub's rate limit. waiting for a few seconds and resuming with username - \"{username}\"")
            time.sleep(rate_limit_sleep_seconds)
            continue
        else:
            r.raise_for_status()

        return True


def _execute_command(command, raise_on_failure=True, working_directory=None, environment_variables=None):
    process = subprocess.Popen(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE, cwd=working_directory, env=environment_variables)
    stdout, stderr = process.communicate()
    exit_code = process.wait()
    command_string = ' '.join(command)

    stdout = stdout.decode("utf-8")
    stderr = stderr.decode("utf-8")

    if raise_on_failure and exit_code != 0:
        command_string = ' '.join(command)
        raise Exception(f'Failed executing command="{command_string}" exit code="{exit_code}" stderr="{stderr}" stdout="{stdout}"')

    logger.debug(f'Executed command="{command_string}" exit code="{exit_code}" stderr="{stderr}" stdout="{stdout}"')
    return stdout, stderr, exit_code


def _locate_go_package_dir_path(go_package_url, go_packages_dir_path):
    if '@' in go_package_url:
        go_package_url = go_package_url.split('@')[0]
    expected_path = os.path.join(go_packages_dir_path, go_package_url)
    for root, dirs, files in os.walk(go_packages_dir_path):
        root_path_no_version = root.split('@')[0]
        if root_path_no_version == _normalize_go_package_path(expected_path):
            package_path_version_suffix = root.split('@')[1].split('/')[0]
            return f'{root_path_no_version}@{package_path_version_suffix}'


def _normalize_go_package_path(path):
    match = re.findall(r'[A-Z]', path)
    for item in match:
        path = path.replace(item, f'!{item.lower()}')
    return path


def _normalize_go_package(go_package_dir_path, environment_variables):
    go_package_dir_files = os.listdir(go_package_dir_path)
    if 'go.mod' not in go_package_dir_files:
        go_init_command = ["go", "mod", "init", "mod"]
        _execute_command(go_init_command, working_directory=go_package_dir_path, environment_variables=environment_variables)

    if 'go.sum' not in go_package_dir_files:
        go_tidy_command = ["go", "mod", "tidy", "-e"]
        _execute_command(go_tidy_command, working_directory=go_package_dir_path, environment_variables=environment_variables)


def _parse_go_mod_graph_command_output(graph_output):
    lines = graph_output.splitlines()
    github_usernames = set()
    go_packages = set()
    for line in lines:
        go_package = line.strip().split()[1]
        go_packages.add(go_package)
        go_package_parts = go_package.split('/')
        if go_package_parts[0] == 'github.com':
            github_usernames.add(go_package_parts[1])

    return go_packages, github_usernames


def _filter_vulnerable_go_packages(go_packages, vulnerable_usernames):
    for go_package in go_packages:
        go_package_parts = go_package.split('/')

        if len(go_package_parts) < 2:
            logger.debug(f'Ignoring go package="{go_package}" as it does not appear to be a valid record')
            continue

        go_package_username = go_package_parts[1]
        if go_package_username not in vulnerable_usernames:
            logger.debug(f"Ignoring go package=\"{go_package}\" as it's username does not appear to be vulnerable")
            continue

        logger.debug(f"{go_package} can be hijacked")
        yield go_package


def _scan_go_package(go_package_dir_path, environment_variables, github_token, raise_on_failure=True):
    _normalize_go_package(go_package_dir_path, environment_variables)

    try:
        go_graph_command = ["go", "mod", "graph"]
        stdout, _, _ = _execute_command(go_graph_command, working_directory=go_package_dir_path, environment_variables=environment_variables)
        go_packages, github_usernames = _parse_go_mod_graph_command_output(stdout)

        vulnerable_github_usernames = set()
        for username in github_usernames:
            if not _is_github_username_exists(username, github_token):
                vulnerable_github_usernames.add(username)

        vulnerable_go_packages = _filter_vulnerable_go_packages(go_packages, vulnerable_github_usernames)
        vulnerable_go_packages = list(vulnerable_go_packages)
        return vulnerable_go_packages

    except Exception:
        logging.debug(f'failed to analyze package {go_package_dir_path}', exc_info=True)
        return []


def scan(go_packages, github_token):
    temp_dir_path = tempfile.mkdtemp()
    vulnerable_dependencies = []
    try:
        environment_variables = os.environ.copy()
        environment_variables['GOPATH'] = temp_dir_path

        for go_package in go_packages:
            logger.debug(f'Scanning "{go_package}" ...')

            if os.path.isdir(go_package):
                go_package = os.path.realpath(go_package)
                go_package_dir_path = go_package
                shutil.copytree(go_package_dir_path, os.path.join(temp_dir_path, 'mod'), copy_function=shutil.copyfile)
                temp_go_package_dir = os.path.join(temp_dir_path, 'mod')
            else:
                go_package_url = go_package
                go_get_command = ['go', 'get', '-d', '-modcacherw', go_package_url]
                _execute_command(go_get_command, working_directory=temp_dir_path, environment_variables=environment_variables)

                go_packages_dir_path = os.path.join(temp_dir_path, 'pkg', 'mod')
                downloaded_package_dir = _locate_go_package_dir_path(go_package_url, go_packages_dir_path)

                temp_go_package_dir = os.path.join(temp_dir_path, 'mod')
                shutil.copytree(downloaded_package_dir, temp_go_package_dir, copy_function=shutil.copyfile)

            logger.debug(f'Scanning "{temp_go_package_dir}" ...')
            partial_vulnerable_dependencies = _scan_go_package(temp_go_package_dir, environment_variables, github_token)
            vulnerable_dependencies.extend(partial_vulnerable_dependencies)
    finally:
        try:
            shutil.rmtree(temp_dir_path)
        except OSError:
            logger.warning(f'Failed to clear temporary directory="{temp_dir_path}" (permission issue). please manually delete it')

    return vulnerable_dependencies
