
import plotly

# pass a dict mapping colors to lists of lat-lng pairs
# example:
# usa_map( point_dict = {
#     'red' : [ (lat1,lng1), ... ],
#     'blue' : [ ... ],
# } )
def usa_map ( point_dict={ }, title='Points on USA Map' ):
    # the following line is in case they send me a zip() object
    munged = { key : [ list(a) for a in point_dict[key] ] for key in point_dict }
    # make the plot
    return plotly.offline.iplot(
        plotly.graph_objs.Figure(
            # the layout
            layout = plotly.graph_objs.Layout(
                title = title,
                geo = {
                    'scope' : 'usa',
                    'projection' : { 'type' : 'albers usa' },
                    'showland' : True,
                    'landcolor' : '#9a9'
                },
                showlegend = False
            ),
            # the data as a set of sets of points, each outer set assigned a color
            data = [
                plotly.graph_objs.Scattergeo(
                    locationmode = 'USA-states',
                    mode = 'markers',
                    lat = [ list( point )[0] for point in munged[color] ],
                    lon = [ list( point )[1] for point in munged[color] ],
                    marker = { 'size' : 5, 'color' : color, 'opacity' : 1.0, 'line' : { 'width' : 0 } }
                )
                for color in munged
            ]
        )
    )
