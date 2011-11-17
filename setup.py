#!/usr/bin/env python

import os
import sys
import codecs

try:
    from setuptools import setup, Command, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, Command, find_packages  # noqa
from distutils.command.install import INSTALL_SCHEMES

src_dir = "django_kissmetrics"

class RunTests(Command):
    description = "Run the django test suite from the tests dir."
    user_options = []
    extra_env = {}
    extra_args = []

    def run(self):
        for env_name, env_value in self.extra_env.items():
            os.environ[env_name] = str(env_value)

        this_dir = os.getcwd()
        testproj_dir = os.path.join(this_dir, "tests")
        os.chdir(testproj_dir)
        sys.path.append(testproj_dir)
        from django.core.management import execute_manager
        os.environ["DJANGO_SETTINGS_MODULE"] = os.environ.get(
                        "DJANGO_SETTINGS_MODULE", "settings")
        settings_file = os.environ["DJANGO_SETTINGS_MODULE"]
        settings_mod = __import__(settings_file, {}, {}, [''])
        prev_argv = list(sys.argv)
        try:
            sys.argv = [__file__, "test"] + self.extra_args
            execute_manager(settings_mod, argv=sys.argv)
        finally:
            sys.argv = prev_argv

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass


class QuickRunTests(RunTests):
    extra_env = dict(SKIP_RLIMITS=1, QUICKTEST=1)

if os.path.exists("README.rst"):
    long_description = codecs.open("README.rst", "r", "utf-8").read()
else:
    long_description = "See https://github.com/votizen/django-kissmetrics"

setup(
    name = 'django-kissmetrics',
    packages=find_packages(),
    version='.'.join(map(str, __import__('django_kissmetrics').__version__)),
#    version='0.2.4',
    description = 'Tool for working with KISSmetrics in Django.',
    long_description = long_description,
    url = 'http://github.com/votizen/django-kissmetrics',
    author = 'Matt Snider',
    author_email = 'msnider@votizen.com',
    maintainer = 'Matt Snider',
    maintainer_email = 'msnider@votizen.com',
    keywords = ['kissmetrics', 'django'],
    license = 'MIT',
    cmdclass={
        "test": RunTests,
        "quicktest": QuickRunTests
    },
    include_package_data=True,
    platforms=["any"],
    classifiers=[
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)