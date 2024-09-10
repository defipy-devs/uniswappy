from setuptools import setup

with open('README.md') as f:
    long_description = f.read()

setup(name='UniswapPy',
      version='1.5.6',
      description='Uniswap Analytics with Python',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://github.com/defipy-devs/uniswappy',
      author = "icmoore",
      author_email = "defipy.devs@gmail.com",
      license='MIT',
      package_dir = {"uniswappy": "python/prod"},
      packages=[
          'uniswappy',
          'uniswappy.cpt.exchg',
          'uniswappy.cpt.factory',
          'uniswappy.cpt.index',
          'uniswappy.cpt.quote',
          'uniswappy.cpt.vault',
          'uniswappy.cpt.wallet',
          'uniswappy.erc',
          'uniswappy.math.basic',
          'uniswappy.math.interest',
          'uniswappy.math.interest.ips',
          'uniswappy.math.interest.ips.aggregate',
          'uniswappy.math.model',
          'uniswappy.math.risk',
          'uniswappy.process',
          'uniswappy.process.burn',
          'uniswappy.process.deposit',
          'uniswappy.process.liquidity',
          'uniswappy.process.mint',
          'uniswappy.process.swap',
          'uniswappy.process.join',
          'uniswappy.simulate',
          'uniswappy.utils.interfaces',
          'uniswappy.utils.data',
          'uniswappy.utils.client',
          'uniswappy.utils.tools',
          'uniswappy.utils.tools.v3'
      ],
      install_requires=[
          'scipy >= 1.7.3',
          'termcolor >= 2.4.0'
      ],
      zip_safe=False)
