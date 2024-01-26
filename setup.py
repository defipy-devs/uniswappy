from setuptools import setup

with open('README.md') as f:
    long_description = f.read()

setup(name='UniswapPy',
      version='1.1.0',
      description='Uniswap for Python',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='http://github.com/icmoore/uniswappy',
      author = "icmoore",
      author_email = "utiliwire@gmail.org",
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
          'uniswappy.simulate'
      ],
      install_requires=[
          'scipy >= 1.7.3'
      ],
      zip_safe=False)
