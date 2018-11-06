import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import datetime
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import sys
sys.path.append('lib')
sys.path.append('rainfall data')
import projectCode as pc
import seaborn as sns

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# dash app
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

#read and tally data
hrs = 48
d_df = pc.readModelData(hrs)
b_df = pc.readBaselineData(hrs)
b_df = pc.prepBaselineDF(b_df)

#d_df
d_df = pc.sumPredictedTotals(d_df)
d_df = pc.prepDF(d_df) 
d_df = pc.aggregateData(d_df)
d_df = pc.setRainfallDelta(b_df, d_df)
c_df  = d_df[['LAT', 'LON', 'ReturnPeriod', 'Radiation', 'TimeFrame', 'rainfallChange', 'rainfallPctChange']]
c_df = c_df.sort_values(by=['LAT', 'LON'], ascending=[False, True])

app.layout = html.Div([
	html.Div([

		html.Div([
			# dropdown menu for returnperiod
		dcc.Dropdown(
				id='ReturnPeriod',
				# dropdown options
				options=[{'label': i, 'value': i} for i in c_df['ReturnPeriod'].unique()],
				# default value
				value = 10
			),
		# dropdown menu for radiation
		dcc.Dropdown(
				id='Radiation',
				options=[{'label': i, 'value': i} for i in c_df['Radiation'].unique()],
				value='8.5'
			)

		],
		style={'width': '49%', 'display': 'inline-block'}),

		html.Div([
			# dropdown menu for 2050/2080
			dcc.Dropdown(
				id='TimeFrame',
				options=[{'label': i, 'value': i} for i in c_df['TimeFrame'].unique()],
				value='2050'
			),
			# dropdown menu for rainfallchange/rainfallPctChange
			dcc.Dropdown(
				id='vals',
				options=[{'label': i, 'value': i} for i in ['rainfallChange', 'rainfallPctChange']],
				value='rainfallChange'
			)
		], style={'width': '49%', 'float': 'right', 'display': 'inline-block'})
	], style={
		'borderBottom': 'thin lightgrey solid',
		'backgroundColor': 'rgb(250, 250, 250)',
		'padding': '10px 5px'
	}),
# graph object, identified by Output through 'id'
	html.Div([
		dcc.Graph(
			id='crossfilter-indicator-heatmap',
			)
		# styles: width, display, etc
	], style={'width': '60%', 'display': 'inline-block', 'padding': '0 20'})
])


# custom function to get pivot table, used in update_graph
def get_pivot_table(f_df, returnPeriod, Radiation, timeframe,vals):
	#filter to selected data for the heatmap
	timeframe = str(timeframe)

	df = f_df[(f_df.ReturnPeriod == returnPeriod) & (f_df.Radiation == Radiation) & (f_df.TimeFrame == timeframe)]
	#pivot on location with rainfallChange

	df_wide = df.pivot_table(index = 'LAT', 
		columns = 'LON', 
		values = vals)
	#sort the results
	df_wide.sort_index(level = 0, ascending=False, inplace = True)

	#generateHeatMap
	return df_wide

# callbacks for updating graph. specifies I/O
@app.callback(
	dash.dependencies.Output('crossfilter-indicator-heatmap', 'figure'),
	# inputs corresponds to the dropdown menus, as indicated by their id
	[dash.dependencies.Input('ReturnPeriod', 'value'),
		dash.dependencies.Input('Radiation', 'value'),
		dash.dependencies.Input('TimeFrame', 'value'),
		dash.dependencies.Input('vals', 'value')])

# updates dcc.Graph
def update_graph(ReturnPeriod, Radiation,
				 TimeFrame, vals):
	return {
		'data' :[go.Heatmap(
			x=get_pivot_table(f_df = c_df,
				returnPeriod = ReturnPeriod,
				Radiation = Radiation,
				timeframe = TimeFrame,
				vals = vals).columns,
			y=get_pivot_table(f_df = c_df,
				returnPeriod = ReturnPeriod,
				Radiation = Radiation,
				timeframe = TimeFrame,
				vals = vals).index,
			z = get_pivot_table(f_df = c_df,
				returnPeriod = ReturnPeriod,
				Radiation = Radiation,
				timeframe = TimeFrame,
				vals = vals).values,
			# sets colorscale
			colorscale=[[0.0, 'rgb(165,0,38)'], [0.1111111111111111, 'rgb(215,48,39)'], 
		[0.2222222222222222, 'rgb(244,109,67)'], [0.3333333333333333, 'rgb(253,174,97)'],
		 [0.4444444444444444, 'rgb(254,224,144)'], [0.5555555555555556, 'rgb(224,243,248)'], [0.6666666666666666, 'rgb(171,217,233)'],
		 [0.7777777777777778, 'rgb(116,173,209)'], [0.8888888888888888, 'rgb(69,117,180)'], [1.0, 'rgb(49,54,149)']]
		),

		],
		'layout': go.Layout(
            margin={'l': 40, 'b': 30, 't': 10, 'r': 0},
            height=800,
            hovermode='closest'
        )
	}



if __name__ == '__main__':
	app.run_server()