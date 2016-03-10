from bokeh.models.widgets import Button
from bokeh.client import push_session
from bokeh.plotting import figure, curdoc
from bokeh.io import vform, hplot

figure_obj  = figure()
button = Button(label = "this thing")

hplot(figure_obj, button)

session = push_session(curdoc())
session.show()
session.loop_until_closed()


