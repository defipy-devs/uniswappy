# DeFi Quant Terminal
This application uses the live API data to produce a mock Uniswap pool which allows end-users to stress test
the limitations of a Uniswap pool setup.

## Local Installation 

Install project requirements:
```
> git clone https://github.com/defipy-devs/uniswappy/tree/ethdenver
> pip install -r requirements.txt

```

Next, install modified ETHDenver GH instance of Uniswappy python package: 
```
> pip install .
```

## Run application locally  

```
> bokeh serve --show python/application/bokeh_server.py
``` 
		

## Technical References 
 * **Reblancing Pool**: 
     * Math behind rebalancing pool upon price change
     * See [How to Simulate a Uniswap Pool](https://medium.com/@icmoore/simulating-a-liquidity-pool-for-decentralized-finance-6f357ec8564b)
  * **Indexed Liquidity**: 
      * Monitoring profitability of swap positions
      * See [The Uniswap Indexing Problem](https://medium.com/datadriveninvestor/the-uniswap-indexing-problem-8078b8b110fc)
   * **Impermanent Loss**: 
       * How variance impacts impermanent loss
       * See (Eq. 6) [Technical Survey of Impermanent Loss](https://github.com/icmoore/impermanent_loss/blob/main/article.pdf)
 
 
