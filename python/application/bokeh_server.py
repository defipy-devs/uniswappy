from bokeh.plotting import figure, curdoc, show
from bokeh.models import ColumnDataSource, Button, Spacer, FuncTickFormatter, Select, HoverTool, GridPlot, Div, Styles
from bokeh.layouts import gridplot, column, row, layout
from uniswappy import *
import time
from datetime import datetime


### Init vars ###

# Theme 
curdoc().theme = 'dark_minimal'
current_theme_is_dark = True
dark_style = Styles(
    display="flex",  # Use flexbox layout
    justify_content="center",  # Center horizontally in the flex container
    align_items="center",  # Center vertically in the flex container
    height="100px",  # Set a height for the Div to see the vertical centering effect
    text_align="center", 
    width="100%",
    font_size="20px",
    background_color="#21262a",
    color = "white" 
)
button_dark_style = Styles(  
    justify_content="center",  # Center horizontally in the flex container
    align_items="center",  # Center vertically in the flex container
    height="100px",  # Set a height for the Div to see the vertical centering effect
    text_align="center", 
    width="100%",
    font_size="20px",
    background_color="#21262a",
    color = "white" 
)
light_style = Styles(
    display="flex",  # Use flexbox layout
    justify_content="center",  # Center horizontally in the flex container
    align_items="center",  # Center vertically in the flex container
    height="100px",  # Set a height for the Div to see the vertical centering effect
    text_align="center", 
    width="100%",
    font_size="20px",
    background_color="#fff",
    color = "black"
)
button_light_style = Styles(
    justify_content="center",  # Center horizontally in the flex container
    align_items="center",  # Center vertically in the flex container
    height="100px",  # Set a height for the Div to see the vertical centering effect
    text_align="center", 
    width="100%",
    font_size="20px",
    background_color="#fff",
    color = "black"
)

# Time 
timestamp_counter = 0
rate = 3

# # -------------------
# # Canonical Settings
# # -------------------

# Default values
chain_api = Chain0x.ETHEREUM
stable = Chain0x.USDC
token = Chain0x.WETH

max_trade_percent = 0.001 # lower means less volatility
time_window = 0.25 # how often sim runs and 0x API is pinged
trade_bias = 0.5 # bias between stable and token swaps (50/50)

# intialize chain and API with default values
chain = Chain0x(buy_tkn_nm = token, sell_tkn_nm = stable, max_trade_percent = max_trade_percent, time_window = time_window, trade_bias = trade_bias)
api = API0x(chain = chain_api)
# -------------------
# ETHDenverSim
# -------------------

init = False
callback_id = None
div = Div(text="Last updated at:")
instructions = Div(text="First choose a network and token/stablecoin pair. Next click ""Start Simulation"" to begin modelling", styles=dark_style)

# sim = ETHDenverSimulator() # default mode
sim = ETHDenverSimulator(buy_token = chain.get_buy_token(),
                         sell_token = chain.get_sell_token(),
                         time_window = time_window,
                         trade_bias = trade_bias,
                         td_model = chain.get_td_model(),
                         api = api)

### Functions ###

# Dark/Light mode button
def switch_theme(event):
    global current_theme_is_dark, instructions, button_row  # Declare the variable as global to modify it
    
    # Toggle the theme based on the current state
    if current_theme_is_dark:
        curdoc().theme = 'light_minimal'
        new_theme = 'light_minimal'
        toggle_button.label = "Dark Mode"
        toggle_button.button_type = "primary"
        instructions.styles=light_style
        button_row.styles=light_style
    else:
        curdoc().theme = 'dark_minimal'
        new_theme = 'dark_minimal'
        toggle_button.label = "Light Mode"
        toggle_button.button_type = "default"
        instructions.styles=dark_style
        button_row.styles=dark_style
    
    # Toggle the flag
    current_theme_is_dark = not current_theme_is_dark

    # Print statements for debugging
    print(f"Theme changed to {new_theme}")

# Start/Stop button
def initialize_sim(event):
    global init, callback_id

    # sim.init_lp(init_x_tkn = bnb_init_amt, x_tkn_nm = bnb_tkn_nm)
    sim.init_lp(init_x_tkn = chain.get_buy_init_amt(), 
            x_tkn_nm = chain.buy_tkn_nm, 
            init_x_invest = chain.init_investment)

    if init:
        # Simulation is currently running, so stop it
        if callback_id:
            curdoc().remove_periodic_callback(callback_id)
            callback_id = None
        init_button.label = "Start Simulation"  # Update button label
        init_button.button_type = "success"
        print("Sim stopped")
    else:
        # Simulation is currently stopped, so start it
        callback_id = curdoc().add_periodic_callback(update_data, rate * 1000)
        init_button.label = "Stop Simulation"  # Update button label
        init_button.button_type = "danger"
        print("Sim started")
    
    init = not init  # Toggle the state
    
def refresh_sim(event):
    global chain, sim
    chain = Chain0x(buy_tkn_nm = token, sell_tkn_nm = stable)
    api = API0x(chain = chain_api)
    sim = ETHDenverSimulator(buy_token = chain.get_buy_token(),
                         sell_token = chain.get_sell_token(),
                         time_window = time_window,
                         trade_bias = trade_bias,
                         td_model = chain.get_td_model(),
                         api = api)
    sim.init_lp(init_x_tkn = chain.get_buy_init_amt(), 
            x_tkn_nm = chain.buy_tkn_nm, 
            init_x_invest = chain.init_investment)
    print("Sim refreshed \n")
    clear_data()
    

# Chain drop down selection function
def chain_selection(attr, old, new):
    global chain_api, chain_nm
    Chain0x.chain_nm = new
    chain_api = Chain0x.chain_nm
    print(f"Selected chain: {chain_api}")
    refresh_sim(None)

# Token drop down selection function
def token_selection(attr, old, new):
    global token, buy_tkn_nm
    Chain0x.buy_tkn_nm = new
    token = Chain0x.buy_tkn_nm
    print(f"Selected crypto: {token}")
    refresh_sim(None)
    # if not init:
    #     refresh_sim(None)

# Stable coin drop down selection function
def stable_selection(attr, old, new):
    global stable, sell_tkn_nm
    Chain0x.sell_tkn_nm = new
    stable = Chain0x.sell_tkn_nm
    print(f"Selected stable: {stable}")
    refresh_sim(None)

def initiate_charts():
    global p1, p2, p3, p4, grid
    # Initialize Bokeh figures and data sources
    p1 = figure(title=f'Price of Token in Stablecoin & LP Price Deviation', x_axis_label='Time', y_axis_label='Price ($)', width_policy='max', height_policy='max')
    p1.line(x='x', y='y', source=source1, color='green', legend_label='Market Price')
    # p1.line(x='x', y='lp_arb', source=source1, color='green', legend_label='LP Arb Price')
    p1.line(x='x', y='lp_swap', source=source1, color='blue', legend_label='Liquidity Pool Price')
    p1.toolbar.logo = None

    p2 = figure(title=f'Token Reserve', x_axis_label='Time', y_axis_label=f'Reserve (Token)', width_policy='max', height_policy='max')
    p2.line(x='x', y='x_swap', source=source2, color='blue', legend_label='Pool Deviation')
    p2.line(x='x', y='x_arb', source=source2, color='green', legend_label=f'Token Reserves')
    p2.toolbar.logo = None

    p3 = figure(title=f'Stable Reserve', x_axis_label='Time', y_axis_label=f'Reserve (Stablecoin)', width_policy='max', height_policy='max')
    p3.line(x='x', y='y_swap', source=source3, color='blue', legend_label='Pool Deviation')
    p3.line(x='x', y='y_arb', source=source3, color='green', legend_label=f'Stable Reserves')
    p3.toolbar.logo = None

    p4 = figure(title='Health Indicator (Swap Amounts)', x_axis_label='Time', y_axis_label=f'Amount of Token per Swap', width_policy='max', height_policy='max')
    p4.line(x='x', y='y', source=source4, color='red', legend_label='Swap Amount')
    p4.toolbar.logo = None

    # Create a custom tick formatter script
    formatter_script_dollar = """
    if (tick >= 1e6) {
        return '$' + (tick / 1e6).toFixed(2) + 'M';
    } else if (tick >= 1e4) {
        return '$' + (tick / 1e3).toFixed(2) + 'K';
    } else {
        return '$' + tick.toFixed(2);
    }
    """

    formatter_script_eth = """
    if (tick >= 1e6) {
        return (tick / 1e6).toFixed(2) + 'M';
    } else if (tick >= 1e4) {
        return (tick / 1e3).toFixed(2) + 'K';
    } else {
        return tick.toFixed(2);
    }
    """

    # Create the formatter
    custom_formatter_dollar = FuncTickFormatter(code=formatter_script_dollar)

    custom_formatter_eth = FuncTickFormatter(code=formatter_script_eth)

    # Apply this formatter to the y-axis of each of your plots
    p1.yaxis.formatter = custom_formatter_dollar
    p2.yaxis.formatter = custom_formatter_eth
    p3.yaxis.formatter = custom_formatter_dollar

    ### Running  Code ###

    # Create a grid layout with the plots
    grid = gridplot([[p1, p2], [p3, p4]], sizing_mode='stretch_both')

# Refresh graphs function
def update_data():
    global timestamp_counter, div

    div.text = f"Last updated at: {datetime.now()}"

    price = sim.trial() # initiate each trial run

    print("Price: ", price)
    
    # Arbitration and Swapping timestamps (Swap always comes first, one of each returned per trial)
    arbtime = sim.get_time_stamp(ETHDenverSimulator.STATE_ARB)
    swaptime = sim.get_time_stamp(ETHDenverSimulator.STATE_SWAP)

    # X Reserve Plot (WETH)
    x_swap = sim.get_x_reserve(ETHDenverSimulator.STATE_SWAP)
    x_arb = sim.get_x_reserve(ETHDenverSimulator.STATE_ARB)

    # Y Reserve Plot (USDC)
    y_swap = sim.get_y_reserve(ETHDenverSimulator.STATE_SWAP)
    y_arb = sim.get_y_reserve(ETHDenverSimulator.STATE_ARB)

    # LP Price Deviation Overlay
    lp_swap = sim.get_lp_price(ETHDenverSimulator.STATE_SWAP)
    # lp_arb = sim.get_lp_price(ETHDenverSimulator.STATE_ARB)
    
    # print("LP ARB: ", lp_arb)
    print("LP Swap: ", lp_swap,"\n")
    
    # Health Indicator - Measures Swap Amounts Over Time (Gives user an idea for how much users should be allowed to swap at once)
    swap_amt = sim.get_swap_amt()

    # Update Bokeh data sources
    source1.stream({'x': [timestamp_counter], 'y': [price], 'lp_swap': [lp_swap]}, rollover=1000)
    source2.stream({'x': [timestamp_counter], 'x_swap': [x_swap], 'x_arb': [x_arb]}, rollover=1000)
    source3.stream({'x': [timestamp_counter], 'y_swap': [y_swap], 'y_arb': [y_arb]}, rollover=1000)
    source4.stream({'x': [timestamp_counter], 'y': [swap_amt]}, rollover=1000)

    timestamp_counter += rate

def clear_data():
    source1.data = {'x': [], 'y': [], 'lp_swap': []}
    source2.data = {'x': [], 'x_swap': [], 'x_arb': []}
    source3.data = {'x': [], 'y_swap': [], 'y_arb': []}
    source4.data = {'x': [], 'y': []}
    print("Data cleared")

### Initialize Chart Data ####

# Create Initialize button
init_button = Button(label="Start Simulation", button_type="success", width=200)
init_button.on_click(initialize_sim)

# Create reinitialize button
# refresh_button = Button(label="Refresh Simulation Data", button_type="success", width=200)
# refresh_button.on_click(refresh_sim)

# Create the toggle button
toggle_button = Button(label="Light Mode", button_type="default", width=200)
toggle_button.on_click(switch_theme)

# Create chain selection dropdown
select_chain = Select(title="Choose Network (Default ETH Mainnet):", value="ETHEREUM", options=["ETHEREUM", "ARBITRUM", "AVALANCHE", "BASE", "BINANCE", "CELO", "FANTOM", "OPTIMISM", "POLYGON"])
select_chain.on_change('value', chain_selection)

# Create token selection dropdown
select_token = Select(title="Choose Token (Default WETH):", value="WETH", options=["WETH", "LINK", "UNI", "WBTC", "BNB"])
select_token.on_change('value', token_selection)

# Create stable token selection dropdown
select_stable = Select(title="Choose Stablecoin (Default USDC):", value="USDC", options=["USDC", "USDT", "DAI"])
select_stable.on_change('value', stable_selection)

source1 = ColumnDataSource(data={'x': [], 'y': [], 'lp_swap': []})  # For Buy (WETH)/ Sell (USDC) Price and LP Price Deviation
source2 = ColumnDataSource(data={'x': [], 'x_swap': [], 'x_arb': []})  # For X Reserve (e.g., WETH)
source3 = ColumnDataSource(data={'x': [], 'y_swap': [], 'y_arb': []})  # For Y Reserve (e.g., USDC)
source4 = ColumnDataSource(data={'x': [], 'y': []})  # For Health Indicator

# Define UI on top of screen
button_row = row(init_button, Spacer(width_policy='max'), select_chain, select_token, select_stable, Spacer(width_policy='max'), toggle_button, sizing_mode='stretch_width', styles=dark_style) 

# add elements to UI
curdoc().add_root(button_row) 
curdoc().add_root(instructions) 


# Define chart appearance and add to UI
initiate_charts()
curdoc().add_root(grid)

