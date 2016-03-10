from bokeh.plotting import figure, curdoc
from bokeh.models import HoverTool, TapTool, BoxZoomTool, BoxSelectTool, PreviewSaveTool, ResetTool
from bokeh.models.widgets import Panel, Tabs, TextInput, RadioGroup
from bokeh.client import push_session
from bokeh.models.sources import ColumnDataSource
from bokeh.io import vform, hplot
from bokeh.palettes import Spectral11

import numpy as np

tabs = []

x = np.linspace(-2*np.pi, 2*np.pi, 200)

colour_list = Spectral11 #[(51, 153, 51) ,(153, 51, 51), (51, 51, 153), (153, 51,153 ), (153, 51, 51)]



y = np.sin(x)
w = np.cos(x)

a = ColumnDataSource(dict(x = x, y = y))
b = ColumnDataSource(dict(x = x, y = w))

z = np.arcsin(x)
u = np.arccos(x)

c = ColumnDataSource(dict(x = x, y = z))
d = ColumnDataSource(dict(x = x, y = u))


v = np.arctan(x)
r = np.tan(x)

e = ColumnDataSource(dict(x = x, y = v))
f = ColumnDataSource(dict(x = x, y = r))

list_of_axis = [(a, b), (c,d), (e, f)]

hover = HoverTool(
tooltips=[
	("(x,y)", "($x, $y)"),
])

Tools = [ TapTool(), BoxZoomTool(), BoxSelectTool(), PreviewSaveTool(), ResetTool()]




def update_title(new, radio, sources):

	print("hello")
	active_source = sources[radio.active]
	factor = float(new)

	x = active_source.data["x"]
	y = factor*active_source.data["y"]

	active_source.data = dict(x = x, y = y)


for two in list_of_axis: 

	figure_obj = figure(plot_width = 1000, plot_height = 800, title = "these are waves", tools = Tools)
	
	#for mytool in Tools:
	#	mytool.plot = figure_obj 

	#figure_obj.tools = Tools

	figure_obj.line("x", "y", source = two[0], line_width = 2, line_color = colour_list[3])
	figure_obj.line("x", "y", source = two[1], line_width = 2, line_color = colour_list[1])

	text = TextInput(title="title", value='my sine wave')
	radio = RadioGroup(labels = ["0", "1"], active = 0)

	text.on_change('value', lambda attr, old, new, radio = radio, sources = two: 
					update_title(new, radio, sources))

	tabs.append(Panel(child = hplot(figure_obj, vform(text, radio)), title = "two by two"))

tabs = Tabs(tabs = tabs)
session = push_session(curdoc())
session.show()
session.loop_until_closed()
