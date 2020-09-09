#import packages
import os
import pandas as pd
import numpy as np
import geopandas
import json
from google.cloud import bigquery

from bokeh.io import output_notebook, show, output_file
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar, NumeralTickFormatter,NumberFormatter
from bokeh.palettes import brewer

from bokeh.io.doc import curdoc
from bokeh.models import Slider, HoverTool, Select, TapTool, CustomJS, ColumnDataSource, TableColumn, DataTable, CDSView, GroupFilter
from bokeh.layouts import widgetbox, row, column, gridplot
from bokeh.models.widgets import TextInput,DateFormatter

# Prepare initial data

# crime_df = pd.read_pickle(r'C:\Users\Tauseef\Downloads\chicago_crime.pkl')
# temp = crime_df.loc[(~crime_df['latitude'].isnull()) | (~crime_df['longitude'].isnull())].copy()
# cg_2019 = temp.loc[temp['year']==2019].copy()

# read 2019 chicago crime data
cg_2019 = pd.read_pickle(r'C:\Users\Tauseef\Downloads\chicago_2019.pkl')
cg_2019['community_area'] = cg_2019['community_area'].astype('int').astype('str')

# aggregated crime data by community and primary type
df1 = pd.DataFrame(cg_2019.groupby(['community_area','primary_type'])['case_number'].count()).reset_index()

agg_data=pd.pivot_table(cg_2019[['community_area','description']],index=["community_area"], aggfunc='count').reset_index()

# Read the geojson map file for city of Chicago
cg = geopandas.read_file(r'C:\Users\Tauseef\Downloads\Boundaries.geojson')

# Set the Coordinate Referance System (crs) for projections
# ESPG code 4326 is also referred to as WGS84 lat-long projection
cg.crs = {'init': 'epsg:4326'}
# Rename columns in geojson map file
#cg_ = cg.rename(columns={'geometry': 'geometry'}).set_geometry('geometry')

# Merge geojson map file with community level aggregated crime data
merged_df = cg.merge(agg_data, how = 'left', right_on='community_area', left_on='area_num_1')

# Bokeh uses geojson formatting, representing geographical features, with json
# Convert to json
merged_json = json.loads(merged_df.to_json())
json_data = json.dumps(merged_json)

# Create a plotting function
def make_plot():
  
  # Use LinearColorMapper that linearly maps a range of numbers into a sequence of colors.
  color_mapper = LinearColorMapper(palette = palette, low = min(agg_data['description']), high = max(agg_data['description']))

  # Create color bar.
  format_tick = NumeralTickFormatter(format='0,0')
  color_bar = ColorBar(color_mapper=color_mapper, label_standoff=18, formatter=format_tick,
                       border_line_color=None, location = (0, 0))
  color_bar.major_label_text_font_size='8pt'
  
  p = figure(title = 'Offence by Neighborhood in Chicago 2019', 
             plot_height = 650, plot_width = 650, toolbar_location = None)
  

  # Add patch renderer to figure. 
  p.patches('xs','ys', source = geosource, fill_color = {'field' : 'description', 'transform' : color_mapper},
          line_color = 'grey', line_width = 0.25, fill_alpha = 1)
  #Add hover tool to view neighborhood stats
  hover = HoverTool(tooltips = [ ('community','@community'),
                               ('community_area#', '@community_area'),
                               ('#crimes', '@description{,}')])
  style(p)
  p.axis.visible = False
  # Specify color bar layout.
  p.add_layout(color_bar, 'right')

  # Add the hover tool to the graph
  p.add_tools(tap,hover)
  
  return p

def style(p):
    #grid
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None
    #p.axis.visible = False
    #p.ygrid.minor_grid_line_color = 'navy'
    #p.ygrid.minor_grid_line_alpha = 0.1
    #p.ygrid.grid_line_alpha = 0.5
    #p.ygrid.grid_line_dash = [6, 4]
    
    #axis lines and label
    p.xaxis.axis_label_text_font_size = '10pt'
    #p.xaxis.axis_label_font_style = 'bold'
    p.xaxis.axis_line_color= None
    p.yaxis.axis_label_text_font_size = '10pt'
    #p.yaxis.axis_label_font_style = 'bold'
    p.yaxis.axis_line_color= None
    
    #tick labels
    p.xaxis.major_label_text_font_size = '8pt'
    p.yaxis.major_label_text_font_size = '8pt'
    p.xaxis.major_tick_line_color = None
    p.yaxis.major_tick_line_color = None
    p.xaxis.minor_tick_line_color = None
    
    #outline
#     p.min_border_left = 5
#     p.outline_line_width = 7
#     p.outline_line_alpha = 0.5
#     p.outline_line_color = "white"
#     p.border_fill_color = "whitesmoke"
    
    #title
    p.title.text_font = "arial"
    #p.title.text_color="black"
    p.title.text_font_style="bold"
    p.title.text_font_size="15px"
    #p.title.background_fill_color="lightgrey"

# On change of source (datatable selection by mouse-click) fill the line items with values by property address
def function_source(attr, old, new):
  selected_index = source.selected.indices[0]
  crime_type = df2.iloc[selected_index]['primary_type']
  subset = df2.loc[df2['primary_type']==crime_type]
  # Merge geojson map file with community level aggregated crime data
  merged_df1 = cg.merge(subset, how = 'left', right_on='community_area', left_on='area_num_1')

  # Bokeh uses geojson formatting, representing geographical features, with json
  # Convert to json
  merged_json1 = json.loads(merged_df1.to_json())
  json_data1 = json.dumps(merged_json1)

  # Input geojson source that contains features for plotting for:
  geosource1 = GeoJSONDataSource(geojson = json_data1)
    
  # Use LinearColorMapper that linearly maps a range of numbers into a sequence of colors.
  color_mapper = LinearColorMapper(palette = palette, low = min(subset['case_number']), high = max(subset['case_number']))
  
  # Create color bar.
  format_tick = NumeralTickFormatter(format='0,0')
  color_bar = ColorBar(color_mapper=color_mapper, label_standoff=18, formatter=format_tick,
                       border_line_color=None, location = (0, 0))
  color_bar.major_label_text_font_size='8pt'

  p = figure(title = ' Offence by Neighborhood in Chicago 2019 - {}'.format(crime_type), 
             plot_height = 650, plot_width = 650, toolbar_location = None)
  
  # Add patch renderer to figure. 
  p.patches('xs','ys', source = geosource1, fill_color = {'field' : 'case_number', 'transform' : color_mapper},
          line_color = 'grey', line_width = 0.25, fill_alpha = 1)
  #Add hover tool to view neighborhood stats
  hover = HoverTool(tooltips = [ ('community','@community'),
                               ('community_area#', '@community_area'),
                               ('#crimes', '@case_number{,}')])
  style(p)
  p.axis.visible = False
  # Specify color bar layout.
  p.add_layout(color_bar, 'right')

  # Add the hover tool to the graph
  p.add_tools(tap,hover)

  layout.children[0] = p
  

# On change of geosource (neighborhood selection by mouse-click) fill the datatable with nieghborhood sales     
def function_geosource(attr, old, new):
    try:
        selected_index = geosource.selected.indices[0]
        subdist = cg.iloc[selected_index]['area_numbe']
        community = cg.loc[cg['area_numbe']==subdist]['community'].values[0]
       
        view1 = CDSView(source=source, filters=[GroupFilter(column_name='community_area', group=subdist)])
        columns = [TableColumn(field = 'primary_type', title = '<b>Crime_Description<b>'),
           TableColumn(field='case_number', title='<b>#Cases<b>', formatter=NumberFormatter(format='0,0'))]
  
        data_table = DataTable(source = source, view = view1, columns = columns, width = 280, height = 500, editable = False,
                               index_position=None)
        p2 = figure(y_range = df2.loc[df2['community_area']==subdist]['primary_type'].unique()[::-1],x_axis_location="above",
                                  title ="Offence count by neighbourhood: {}".format(community), plot_height = 800, plot_width = 1000)
        p2.hbar(y='primary_type', right = 'case_number',source=source,view=view1, height =0.5)
        #p2.xaxis.major_label_orientation = 1.2
        p2.toolbar.active_drag = None
        p2.x_range.start=0
        style(p2)
        p2.outline_line_width = 0
        # Replace the updated datatable in the layout
        layout.children[1] = data_table
        layout.children[2] = p2
        
    except IndexError:
        pass



# Input geojson source that contains features for plotting for:
geosource = GeoJSONDataSource(geojson = json_data)

df2 = pd.DataFrame(cg_2019.groupby(['community_area','primary_type'])['case_number']\
                   .count()).reset_index().sort_values(by = ['community_area','case_number'], ascending=False )

source = ColumnDataSource(df2)

columns = [TableColumn(field = 'primary_type', title = '<b>Crime_Description<b>'),
           TableColumn(field='case_number', title='<b>#Cases<b>',formatter=NumberFormatter(format='0,0'))]
                                     
# Define a sequential multi-hue color palette.
palette = brewer['Blues'][8]

# Reverse color order so that dark blue is highest obesity.
palette = palette[::-1]
 
# Add tap tool to select neighborhood on map
tap = TapTool()

# Call the plotting function for geoplot
p = make_plot()


#Initial data to display in the data table view 
df3 = pd.DataFrame(cg_2019.groupby(['primary_type'])['case_number']\
                   .count()).reset_index().sort_values(by = ['case_number'], ascending=False )
src3 = ColumnDataSource(df3)
# Load the datatable, neighborhood, address, actual price, predicted price and difference for display
data_table = DataTable(source = src3, columns = columns, width = 300, height = 850, editable = False)

# Plot bar chart on loading
p2 = figure(y_range = df3['primary_type'].unique()[::-1],title ="Chicago Offfense Count", x_axis_location="above",
            plot_height = 800, plot_width = 1000)
p2.hbar('primary_type', right = 'case_number',source=src3, height=0.5)
p2.toolbar.active_drag = None
p2.x_range.start=0
style(p2)
p2.outline_line_width = 0
p2.xaxis[0].formatter = NumeralTickFormatter(format="0,0")

# On change of source (datatable selection by mouse-click) fill the line items with values by offence type
source.selected.on_change('indices', function_source)

# On change of geosource (neighborhood selection by mouse-click) fill the datatable with nieghborhood crime offense
geosource.selected.on_change('indices', function_geosource)



# Layout the components with the plot
layout = row(p,data_table,p2)
                             
# Add the layout to the current document
curdoc().add_root(layout)
curdoc().theme='dark_minimal'                    