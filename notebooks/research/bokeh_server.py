from bokeh.plotting import figure, curdoc
from bokeh.models import ColumnDataSource, CustomJS, Range1d, NumeralTickFormatter
from uniswappy.utils.client import API0x
import time
from bokeh.layouts import layout

curdoc().theme = 'dark_minimal'

# Initialize Bokeh figure and data source
p = figure(title='USDC to WETH Price', 
           x_axis_label='Time', y_axis_label='Price', 
           width_policy='max', height_policy='max'
        #    ,background_fill_color="#acadad", border_fill_color="#6d6e6e"
        )
source = ColumnDataSource(data={'x': [], 'y': []})
p.line(x='x', y='y', source=source, line_color='white')

# Toolbar Styling
p.toolbar.logo = None

# # Title Styling
# p.title.text_color = 'white'
# p.title.text_font_style = 'bold'

# # X-axis styling
# p.xaxis.axis_line_color = "white"  # X-axis line color
# p.xaxis.major_tick_line_color = "white"  # X-axis major tick color
# p.xaxis.major_label_text_color = "white"  # X-axis label color

# # Y-axis styling
# p.yaxis.axis_line_color = "white"  # Y-axis line color
# p.yaxis.major_tick_line_color = "white"  # Y-axis major tick color
# p.yaxis.major_label_text_color = "white"  # Y-axis label color


timestamp_counter = 0
timestamp = time.time()

def update_data():
    global timestamp_counter
    api = API0x()
    sell_token = '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48'  # USDC
    buy_token = '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'  # WETH
    sell_amount = 100000000  # 100 USDC (USDC has a base unit of 6)
    data_json = api.apply(sell_token, buy_token, sell_amount)
    
    price = data_json['price']
    price_numeric = float(price)
    # price_numeric = float(price) * 1000000000 # put price in GWEI
    
    # Update data source
    new_data = {'x': [timestamp_counter], 'y': [price_numeric]}
    source.stream(new_data, rollover=100)  # Adjust rollover as needed

    timestamp_counter += 30

    current_time = time.time() - timestamp

    print("Price: ", price_numeric)
    # print("Time: ", current_time)

# Add periodic callback to update data every 30 seconds
curdoc().add_periodic_callback(update_data, 30000)

def adjust_y_range():
    if len(source.data['y']) > 0:
        min_price = min(source.data['y'])
        max_price = max(source.data['y'])
        y_range_min = min_price - 0.1 * min_price
        y_range_max = max_price + 0.1 * max_price
        p.y_range = Range1d(start=y_range_min, end=y_range_max)
        p.yaxis.formatter = NumeralTickFormatter(format='0,0.000000000') 

curdoc().add_periodic_callback(adjust_y_range, 1000)

# Add plot to the document
layout = layout([[p]], sizing_mode='stretch_both')

# Add layout to the document
curdoc().add_root(layout)
