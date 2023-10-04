# UniswapPy
This package is a python re-factor of the original [Uniswap V2 pairing code](https://github.com/Uniswap/v2-core/blob/master/contracts/UniswapV2Pair.sol) and can be 
utilized for the purpose of analysing and modelling its behavior for DeFi

To install package:
```
> git clone https://github.com/icmoore/uniswappy
> pip install .
```
or
```
> pip install UniswapPy
```
# Special Features
 * **Abstracted Actions**: Obfuscation is removed from standard Uniswap action events to help streamline analysis and lower line count
 * **Indexing**: Can calculate settlment LP token amounts given token 
amounts and vice versa 
 * **Simulation**: Can simulate trading using Geometric Brownian Motion (GBM) process, or feed in actual raw price data to analyze behavior
 * **Randomized Events**: Token amount and time delta models to simulate possible trading behavior
 * **Analytical Tools**: Basic yeild calculators and risk tools to assist in analyzing outcomes
