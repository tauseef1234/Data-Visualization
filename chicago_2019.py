import pandas as pd
import numpy as np
import geopandas
import urllib.request
import re, json, pickle
# from google.cloud import bigquery

from bokeh.io import output_notebook, show, output_file
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar, NumeralTickFormatter,NumberFormatter, HTMLTemplateFormatter, Range1d
from bokeh.palettes import brewer

from bokeh.io.doc import curdoc
from bokeh.models import Slider, HoverTool, Panel, Select, TapTool, CustomJS, ColumnDataSource, TableColumn, DataTable, CDSView, GroupFilter
from bokeh.layouts import widgetbox, row, column, gridplot
from bokeh.models.widgets import Paragraph, TextInput, DateFormatter, Div

# Read 2019 chicago crime data
cg_2019 = pickle.load(urllib.request.urlopen("https://github.com/tauseef1234/Data-Visualization/blob/master/data/chicago_2019.pkl?raw=true"))
cg_2019['community_area'] = cg_2019['community_area'].astype('int').astype('str')
cg_2019.sort_values('date',inplace=True)
cg_2019['month'] = cg_2019['date'].dt.month_name().str.upper()
cg_2019['period'] = (cg_2019['date'].dt.hour % 24 + 4)//4
cg_2019['period'].replace({1: 'Late Night',
                      2: 'Early Morning',
                      3: 'Morning',
                      4: 'Noon',
                      5: 'Evening',
                      6: 'Night'}, inplace=True)
cg_2019['day']=cg_2019['date'].dt.weekday_name

months =  list(cg_2019['month'].unique())
offence_type = list(cg_2019['primary_type'].unique())



# Read the geojson map file for city of Chicago
cg = geopandas.read_file('https://raw.githubusercontent.com/tauseef1234/Data-Visualization/master/data/Boundaries.geojson')

def prepare_data():
    subset_data = cg_2019.loc[(cg_2019['month']==month_selection.value) & (cg_2019['primary_type']==offence_selection.value)].copy()
    agg_data=pd.pivot_table(subset_data[['community_area','primary_type']],index=["community_area"], aggfunc='count').reset_index()
    period_data = pd.pivot_table(subset_data[['case_number','day','period']],index=['period'],columns='day',aggfunc='count').replace(np.nan,0)
    df_period = period_data.div(period_data.to_numpy().sum(), axis=1)
    table_df = df_period.append(df_period.sum().rename('Total')).assign(Total=lambda d: d.sum(1)).droplevel(0, axis=1)\
                        .reset_index().rename_axis(None, axis=1)
    bar_data = pd.DataFrame(subset_data.groupby(['period'])['case_number']\
                   .count()).reset_index()
    # Merge geojson map file with community level aggregated crime data
    merged_df = cg.merge(agg_data, how = 'left', right_on='community_area', left_on='area_num_1')
    merged_df.loc[merged_df['community_area'].isnull(),'community_area'] = merged_df['area_num_1']
    merged_df['primary_type'] = merged_df['primary_type'].fillna(0)
    
    # Convert to json
    merged_json = json.loads(merged_df.to_json())
    # Convert to String like object
    json_data = json.dumps(merged_json)
    geosource = GeoJSONDataSource(geojson = json_data)
    return agg_data, geosource, table_df, bar_data
    


# Create a plotting function
def make_plot(agg_data,geosource):
    # Define a sequential multi-hue color palette.
    palette = brewer['Blues'][8]

    # Reverse color order so that dark blue is highest obesity.
    palette = palette[::-1]
  
    # Use LinearColorMapper that linearly maps a range of numbers into a sequence of colors
    if min(agg_data['primary_type'])==max(agg_data['primary_type']):
        color_mapper = LinearColorMapper(palette = palette, low = 0, high = max(agg_data['primary_type']))
    else:
        color_mapper = LinearColorMapper(palette = palette, low = min(agg_data['primary_type']), high = max(agg_data['primary_type']))

    # Create color bar.
    format_tick = NumeralTickFormatter(format='0,0')
    color_bar = ColorBar(color_mapper=color_mapper, label_standoff=10, formatter=format_tick,
                       border_line_color=None, location = (0,0))
    color_bar.major_label_text_font_size='8pt'

    p = figure(title = 'Offence by Neighborhood in Chicago 2019', 
             plot_height = 650, plot_width = 650, toolbar_location = None)


    # Add patch renderer to figure. 
    p.patches('xs','ys', source = geosource, fill_color = {'field' : 'primary_type', 'transform' : color_mapper},
          line_color = 'grey', line_width = 0.25, fill_alpha = 1)
    #Add hover tool to view neighborhood stats
    hover = HoverTool(tooltips = [ ('community','@community'),
                               ('community_area#', '@community_area'),
                               ('#crimes', '@primary_type{,}')])
    style(p)
    p.axis.visible = False
    # Specify color bar layout.
    p.add_layout(color_bar, 'right')

    # Add the hover tool to the graph
    p.add_tools(hover)

    return p

def make_table(table_df):
    
    template="""
                <div style="background:<%= 
                    (function colorfromint(){
                        if( value > 0.05 & value <0.08){
                            return("#bdd7e7")}
                        if( value > 0.08 & value <2){
                            return("#6baed6")}
                        }()) %>; 
                    font-size: 12px;
                    color: black"> 
                    <%= Math.round(value*100) + ' %' %></div>
                """
    template1="""
                <div style="
                    font-size: 12px;
                    color: black"> 
                    <%= value %></div>
                """
    
    source = ColumnDataSource(table_df)
    columns = [TableColumn(field = 'period', title = '<b>Period<b>', formatter=HTMLTemplateFormatter(template=template1)),
               TableColumn(field = 'Monday', title = '<b>Monday<b>', formatter=HTMLTemplateFormatter(template=template)),
               TableColumn(field = 'Tuesday', title = '<b>Tuesday<b>',formatter=HTMLTemplateFormatter(template=template)),
               TableColumn(field = 'Wednesday', title = '<b>Wednesday<b>',formatter=HTMLTemplateFormatter(template=template)),
               TableColumn(field='Thursday', title='<b>Thursday<b>',formatter=HTMLTemplateFormatter(template=template)),
               TableColumn(field = 'Friday', title = '<b>Friday<b>',formatter=HTMLTemplateFormatter(template=template)),
               TableColumn(field = 'Saturday', title = '<b>Saturday<b>',formatter=HTMLTemplateFormatter(template=template)),
               TableColumn(field = 'Sunday', title = '<b>Sunday<b>',formatter=HTMLTemplateFormatter(template=template)),
               TableColumn(field='', title='Total',formatter=HTMLTemplateFormatter(template=template))]
    data_table = DataTable(source = source, columns = columns, width = 800, height = 350, editable = False,
                       index_position=None,row_height=40)
    return data_table

def bar_plot(df):
    src = ColumnDataSource(df)
    p = figure(x_range = df['period'],toolbar_location = None,y_axis_location="right",
    plot_height = 350, plot_width = 800)
    p.vbar(x='period',source=src, top = 'case_number', width=0.3)
    p.y_range.start=0
    return p

# Define styling attributes
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
    
def update_plot(attr,old,new):
    agg_data, geosource, table_df, bar_data = prepare_data()
    # Call the plotting function for geoplot
    fig.children[2] = row(make_plot(agg_data,geosource),column(make_table(table_df),bar_plot(bar_data)))
    
# Set up logo
    
seal = "https://www.chipublib.org/wp-content/uploads/sites/3/2013/07/city-seal.png"
logo_src = ColumnDataSource(dict(url = [seal]))

page_logo = figure(plot_width = 90, plot_height = 90, title="")
page_logo.toolbar.logo = None
page_logo.toolbar_location = None
page_logo.x_range=Range1d(start=0, end=1)
page_logo.y_range=Range1d(start=0, end=1)
page_logo.xaxis.visible = None
page_logo.yaxis.visible = None
page_logo.xgrid.grid_line_color = None
page_logo.ygrid.grid_line_color = None
page_logo.image_url(url='url', x=0.05, y = 0.85, h=0.7, w=0.7, source=logo_src)
page_logo.outline_line_alpha = 0 

# Set up widgets
month_selection = Select(title='Month', options=months, value=months[0], width=200)
offence_selection = Select(title='Offence Type', options=offence_type, value=offence_type[0], width=300)
month_selection.on_change('value',update_plot)
offence_selection.on_change('value',update_plot)


agg_data, geosource, table_df, bar_data = prepare_data()

# Call the plotting function for geoplot
p = make_plot(agg_data,geosource)
table = make_table(table_df)
bar = bar_plot(bar_data)
# Add header to the dashboard
header = Paragraph(text='Chicago Crime Dashboard - 2019', style = {'font-size':'30pt',
                                                            'color':'#1A5276',
                                                            'font-weight':'bold',
                                                            'text_align':'center',
                                                            'font-family':'Arial'},
                                                   width=1000, height=80)
dumdiv = Div(text='               ',width=500)
dumdiv1 = Div(text='               ',width=50)
# Set up plot layout
fig=column(row(dumdiv,page_logo,header), row(month_selection, dumdiv1,offence_selection,dumdiv1), row (p,column(table,bar)))
tab1=Panel(child=fig,title='Offence map')

# Show the plot
curdoc().add_root(fig)