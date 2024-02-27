# 0x API: Live Trading Simulator
This application uses the 0x API to produce a mock Uniswap pool which allows end-users to stress test
the limitations of a Uniswap pool setup using live price feeds

## Local Installation 

Install project requirements:
```
> pip install -r requirements.txt

```

Next, install local python package: 
```
> pip install .
```

## Run application locally  

```
> bokeh serve --show /python/application/bokeh_server.py
```

## Technical References 
 * **Reblancing Pool**: 
     * Math behind rebalancing pool upon price change
     * See article [How to Simulate a Uniswap Pool](https://medium.com/@icmoore/simulating-a-liquidity-pool-for-decentralized-finance-6f357ec8564b)
  * **Indexed Liquidity**: 
      * Monitoring profitability of swap positions
      * See article [The Uniswap Indexing Problem](https://medium.com/datadriveninvestor/the-uniswap-indexing-problem-8078b8b110fc)
   * **Impermanent Loss**: 
       * How variance impacts impermanent loss
       * See article [Technical Survey of Impermanent Loss](https://github.com/icmoore/impermanent_loss/blob/main/article.pdf)
 
 
