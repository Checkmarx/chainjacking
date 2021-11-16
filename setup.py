import json
from codecs import open
from os import path
from setuptools import setup

SCRIPT_DIR = path.abspath(path.dirname(__file__))

with open(path.join(SCRIPT_DIR, 'package.json'), encoding='utf-8') as f:
    package_json = json.load(f)

with open(path.join(SCRIPT_DIR, 'requirements.txt'), encoding='utf-8') as f:
    dependencies = f.readlines()

package_name = package_json['name']
package_version = package_json['version']
package_description = package_json['description']
package_url = package_json['homepage']
package_author_name = package_json['author_name']
package_author_email = package_json['author_email']
package_tags = package_json['tags']
package_license = package_json['license']

with open(path.join(SCRIPT_DIR, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name=package_name,
    python_requires='>=3.6',
    version=package_version,
    description=package_description,
    long_description_content_type='text/markdown',
    long_description=long_description,
    url=package_url,
    author=package_author_name,
    author_email=package_author_email,
    license=package_license,
    test_suite='tests',
    keywords=package_tags,
    packages=[package_name],
    setup_requires=[],
    install_requires=[dependencies]
)
