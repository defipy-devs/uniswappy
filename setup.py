from setuptools import setup

setup(name='daosys-simulator',
      version='0.1',
      description='daosys python simulator',
      package_dir = {"daosys-simulator": "src/python"},
      packages=[
          'daosys-simulator.python'
      ],
      author = "SYSLabs",
      author_email = "imoore@syscoin.org",
      zip_safe=False)
