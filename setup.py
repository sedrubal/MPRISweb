#!/usr/bin/env python

"""
install script
"""

from setuptools import setup, find_packages
import os
import mprisweb
import subprocess


def read(fname):
    """returns the text of a file"""
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def get_requirements(filename="requirements.txt"):
    """returns a list of all requirements"""
    text = read(filename)
    requirements = []
    for line in text.split('\n'):
        req = line.split('#')[0].strip()
        if req != '':
            requirements.append(req)
    return requirements


def get_version():
    """
    returns a version string which is either the current tag or commit hash
    """
    version = subprocess.check_output("git tag -l --contains HEAD", shell=True)
    if version.strip() == '':
        version = subprocess.check_output(
            "git log -n1 --abbrev-commit --format=%h", shell=True)
    return version.strip()

if __name__ == "__main__":
    setup(
        name="MPRISweb",
        packages=find_packages(),
        entry_points={
            "console_scripts": [
                "mprisweb = mprisweb.__main__:main"
            ]
        },
        data_files=[
            ('templates', ['templates/index.html']),
            ('static/css', ['static/css/style.css']),
            ('static/js', [
                'static/js/mprisweb.js',
                'static/js/ui.js',
                'static/js/helper.js',
            ]),
            ('static/img', [
                'static/img/play.svg',
                'static/img/pause.svg',
                'static/img/stop.svg',
            ]),
        ],
        author=mprisweb.__authors__,
        author_email=mprisweb.__email__,
        license=mprisweb.__license__,
        description=mprisweb.__doc__,
        long_description=read("README.md"),
        url=mprisweb.__url__,
        version=get_version(),
        install_requires=get_requirements(),
        classifiers=[
            'Environment :: Web Environment',
            'Framework :: Tornado',
            'Intended Audience :: End User/Desktop',
            'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
            'Natural Language :: English',
            'Operating System :: POSIX :: Linux',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 3',
            'Programming Language :: JavaScript',
            'Topic :: Desktop Environment :: Gnome',
            'Topic :: Desktop Environment :: K Desktop (KDE)',
            'Topic :: Home Automation',
            'Topic :: Internet',
            'Topic :: Multimedia',
            'Topic :: Multimedia :: Sound/Audio',
            'Topic :: Multimedia :: Sound/Audio :: Players',
        ],
    )
