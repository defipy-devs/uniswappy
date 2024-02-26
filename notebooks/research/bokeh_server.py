from bokeh.plotting import figure, curdoc
from bokeh.models import ColumnDataSource, CustomJS, Button, Spacer, FuncTickFormatter
from bokeh.layouts import gridplot, column, row, layout
from bokeh.models.widgets import Div
from uniswappy import *
import time


### Init vars ###

# Theme 
curdoc().theme = 'dark_minimal'
current_theme_is_dark = True

# Time 
timestamp_counter = 0
rate = 3

# Sim
sim = ETHDenverSimulator() # start with default time window
init = False

### Functions ###

def switch_theme(event):
    global current_theme_is_dark  # Declare the variable as global to modify it
    
    # Toggle the theme based on the current state
    if current_theme_is_dark:
        curdoc().theme = 'light_minimal'
        new_theme = 'light_minimal'
    else:
        curdoc().theme = 'dark_minimal'
        new_theme = 'dark_minimal'
    
    # Toggle the flag
    current_theme_is_dark = not current_theme_is_dark

    # Print statements for debugging
    print(f"Theme changed to {new_theme}")

def intialize_sim(event):
    global init
    sim.init_lp(1000)
    init = True
    print("Sim started")

def update_data():
    global timestamp_counter

    price = sim.trial() # meant to be run repeatedly 

    # api = API0x()
    # sell_token = '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48'  # USDC
    # buy_token = '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'  # WETH
    # sell_amount = 10000000  # 10 USDC (USDC has a base unit of 6)
    # data_json = api.apply(sell_token, buy_token, sell_amount)

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
    lp_arb = sim.get_lp_price(ETHDenverSimulator.STATE_ARB)
    
    print("LP ARB: ", lp_arb)
    print("LP Swap: ", lp_swap,"\n")
    
    # Health Indicator - Measures Swap Amounts Over Time (Gives user an idea for how much users should be allowed to swap at once)
    swap_amt = sim.get_swap_amt()

    # Update Bokeh data sources
    source1.stream({'x': [timestamp_counter], 'y': [price], 'lp_arb': [lp_arb], 'lp_swap': [lp_swap]}, rollover=1000)
    source2.stream({'x': [timestamp_counter], 'x_swap': [x_swap], 'x_arb': [x_arb]}, rollover=1000)
    source3.stream({'x': [timestamp_counter], 'y_swap': [y_swap], 'y_arb': [y_arb]}, rollover=1000)
    source4.stream({'x': [timestamp_counter], 'y': [swap_amt]}, rollover=1000)

    timestamp_counter += rate


### Initialize Chart Data ####


# Create Initialize button
init_button = Button(label="Initialize", button_type="primary", width=400)
init_button.on_click(intialize_sim)

# Create the toggle button
toggle_button = Button(label="Toggle Theme", button_type="primary", width=400)
toggle_button.on_click(switch_theme)

button_row = row(init_button, Spacer(width_policy='max'), toggle_button, sizing_mode='stretch_width')

source1 = ColumnDataSource(data={'x': [], 'y': [], 'lp_arb': [], 'lp_swap': []})  # For WETH to USDC Price and LP Price Deviation
source2 = ColumnDataSource(data={'x': [], 'x_swap': [], 'x_arb': []})  # For X Reserve (e.g., WETH)
source3 = ColumnDataSource(data={'x': [], 'y_swap': [], 'y_arb': []})  # For Y Reserve (e.g., USDC)
source4 = ColumnDataSource(data={'x': [], 'y': []})  # For Health Indicator

# Initialize Bokeh figures and data sources
p1 = figure(title='WETH/USDC & LP Price Deviation', x_axis_label='Time', y_axis_label='Price ($)', width_policy='max', height_policy='max')
p1.line(x='x', y='y', source=source1, color='red', legend_label='Market Price')
p1.line(x='x', y='lp_arb', source=source1, color='green', legend_label='LP Arb Price') # Arb Price too close to market price to display in Bokeh
p1.line(x='x', y='lp_swap', source=source1, color='blue', legend_label='LP Swap Price')
p1.toolbar.logo = None

p2 = figure(title='WETH Reserve', x_axis_label='Time', y_axis_label='Reserve (WETH)', width_policy='max', height_policy='max')
p2.line(x='x', y='x_swap', source=source2, color='blue', legend_label='Swap Reserve')
p2.line(x='x', y='x_arb', source=source2, color='green', legend_label='Arb Reserve')
p2.toolbar.logo = None

p3 = figure(title='USDC Reserve', x_axis_label='Time', y_axis_label='Reserve (USDC)', width_policy='max', height_policy='max')
p3.line(x='x', y='y_swap', source=source3, color='blue', legend_label='Swap Reserve')
p3.line(x='x', y='y_arb', source=source3, color='green', legend_label='Arb Reserve')
p3.toolbar.logo = None

p4 = figure(title='Health Indicator (Swap Amounts)', x_axis_label='Time', y_axis_label='Amount (WETH)', width_policy='max', height_policy='max')
p4.line(x='x', y='y', source=source4, color='red', legend_label='Swap Amount')
p4.toolbar.logo = None

# Create a custom tick formatter script
formatter_script = """
if (tick >= 1e6) {
    return '$' + (tick / 1e6).toFixed(2) + 'M';
} else {
    return '$' + tick.toFixed(0);
}
"""

# Create the formatter
custom_formatter = FuncTickFormatter(code=formatter_script)

# Apply this formatter to the y-axis of each of your plots
p1.yaxis.formatter = custom_formatter
p3.yaxis.formatter = custom_formatter

### Running  Code ###

# Add periodic callback to update data every X seconds defined by rate
curdoc().add_periodic_callback(update_data, rate*1000)

# Create a grid layout with the plots
grid = gridplot([[p1, p2], [p3, p4]], sizing_mode='stretch_both')

# Add the final layout to the current document
curdoc().add_root(button_row)
curdoc().add_root(grid)


