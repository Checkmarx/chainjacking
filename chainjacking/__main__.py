import argparse
import logging
import os
import shutil
import sys

from . import logger
from .chainjacking import scan

LOG_MESSAGE_FORMAT = '%(message)s'


def main():
    logging.basicConfig(force=True, level=logging.INFO, format=LOG_MESSAGE_FORMAT)

    # Ensure Go installed
    if shutil.which('go') is None:
        logger.error('Go binaries are not installed. Visit https://golang.org/doc/install')
        sys.exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument('-gt', dest='github_token', help="GitHub token, to run queries on GitHub API (required)", required=True)
    parser.add_argument('-p', dest='path', help="Path to scan. (default=current directory)", default=None)
    parser.add_argument('-v', dest='verbose', help="Verbose output mode", action="store_true")
    parser.add_argument('-url', dest='url', help="Scan one or more GitHub URLs", action='append', nargs='+')
    parser.add_argument('-f', dest='urls', help="Scan one or more GitHub URLs from a file separated by new-line (value = path to a file)")
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(force=True, level=logging.DEBUG, format=LOG_MESSAGE_FORMAT)

    go_modules = []

    if args.url:
        for url in args.url[0]:
            url = url.strip()
            go_modules.append(url)

    elif args.urls:
        with open(args.urls) as f:
            urls = f.readlines()
            urls = map(str.strip, urls)
            go_modules.extend(urls)

    elif args.path:
        go_modules.append(args.path)

    else:
        working_dir_path = os.getcwd()
        go_mod_file_path = os.path.join(working_dir_path, 'go.mod')
        if os.path.isfile(go_mod_file_path):
            go_modules.append(working_dir_path)

    go_modules = filter(str, go_modules)
    go_modules = set(go_modules)
    go_modules = list(go_modules)
    if not go_modules:
        logger.error('There is no go.mod file in your current working directory. if not provided with specific arguments, please run inside a go package directory')
        sys.exit(1)

    vulnerable_dependencies = scan(go_modules, args.github_token)

    has_vulnerable_dependency = False
    for go_package in vulnerable_dependencies:
        logger.error(f'⚠ Go package "{go_package}" is vulnerable to ChainJacking attack')
        has_vulnerable_dependency = True

    if has_vulnerable_dependency:
        sys.exit(1)
    else:
        logger.info('✅ Dependencies analyzed and found to be safe from ChainJacking attacks')


if __name__ == "__main__":
    main()
