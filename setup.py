from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='konform',
      version='0.1.0',
      description='TODO: description',
      long_description=readme(),
      classifiers=[  # https://pypi.org/pypi?%3Aaction=list_classifiers
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Topic :: Software Development :: Quality Assurance',
      ],
      keywords='konform kubernetes kustomize check validation',
      url='http://github.com/openanalytics/konform',
      author='Daan Seynaeve',
      author_email='dseynaeve@openanalytics.eu',
      license='Apache',
      packages=['konform'],
      install_requires=[
          'pyyaml',
      ],
      test_suite='nose.collector',
      tests_require=['nose', 'nose-cover3'],
      entry_points = {
          'console_scripts': ['konform=konform.cmd:main'],
      },
      include_package_data=True,
      zip_safe=False)
