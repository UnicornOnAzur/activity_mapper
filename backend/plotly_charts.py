import plotly.express as px
import plotly.graph_objects as go

def empty_figure(title, height):
    figure = go.Figure()
    figure.update_layout(title=title,
                         height=height)
    return figure
