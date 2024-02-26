from bokeh.plotting import figure, curdoc
from bokeh.models import ColumnDataSource, CustomJS, Button, Spacer
from bokeh.layouts import gridplot, column, row, layout
from bokeh.models.widgets import Div
from uniswappy.utils.client import API0x
import time

curdoc().theme = 'dark_minimal'
# curdoc().theme = 'white_minimal'

current_theme_is_dark = True  # Assumes the initial theme is 'dark_minimal'

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


# Create the toggle button
toggle_button = Button(label="Toggle Theme", button_type="primary", width=400)
toggle_button.on_click(switch_theme)

button_row = row(Spacer(width_policy='max'), toggle_button, sizing_mode='stretch_width', css_classes=['dark-background'])

# Initialize Bokeh figures and data sources
p1 = figure(title='WETH to USDC Price', x_axis_label='Time', y_axis_label='Price', width_policy='max', height_policy='max')
source = ColumnDataSource(data={'x': [], 'y': []})
p1.line(x='x', y='y', source=source)
p1.toolbar.logo = None

p2 = figure(title='WETH to USDC Price', x_axis_label='Time', y_axis_label='Price', width_policy='max', height_policy='max')
p2.line(x='x', y='y', source=source)
p2.toolbar.logo = None

p3 = figure(title='WETH to USDC Price', x_axis_label='Time', y_axis_label='Price', width_policy='max', height_policy='max')
p3.line(x='x', y='y', source=source)
p3.toolbar.logo = None

p4 = figure(title='WETH to USDC Price', x_axis_label='Time', y_axis_label='Price', width_policy='max', height_policy='max')
p4.line(x='x', y='y', source=source)
p4.toolbar.logo = None

timestamp_counter = 0

rate = 6

# Function to update data from API
def update_data():
    global timestamp_counter
    api = API0x()
    sell_token = '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48'  # USDC
    buy_token = '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'  # WETH
    sell_amount = 100000000  # 100 USDC (USDC has a base unit of 6)
    data_json = api.apply(sell_token, buy_token, sell_amount)
    
    price = data_json['price']
    price_numeric = 1/float(price)
    
    # Update data source
    new_data = {'x': [timestamp_counter], 'y': [price_numeric]}
    source.stream(new_data, rollover=100)

    timestamp_counter += rate

# Add periodic callback to update data every X seconds defined by rate
curdoc().add_periodic_callback(update_data, rate*1000)

# Create a grid layout with the plots
grid = gridplot([[p1, p2], [p3, p4]], sizing_mode='stretch_both')

# Add the final layout to the current document
curdoc().add_root(button_row)
curdoc().add_root(grid)


