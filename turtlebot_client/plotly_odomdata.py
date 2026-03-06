import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html


def run_odometry_view(csv_path, ip="127.0.0.1", port=8050, debug=False):

    # Load CSV provided by caller
    df = pd.read_csv(csv_path)

    # Create plot
    fig = px.scatter(
        df,
        x="x",
        y="y",
        title="Odometry Data"
    )

    # Dash app
    app = Dash(__name__)

    app.layout = html.Div([
        html.H1("Odometry Plot"),
        dcc.Graph(
            id="odom-plot",
            figure=fig
        )
    ])

    # Run server
    app.run(
        host=ip,
        port=port,
        debug=debug
    )


# Optional: allow direct running
if __name__ == "__main__":
    run_odometry_view("odom_data.csv")



    """ 

    how to call function:


    from odometry_view import run_odometry_view

run_odometry_view(
    csv_path=r"C:\Users\ramee\OneDrive\Documents\Group Project\odom_data.csv",
    ip="0.0.0.0",
    port=8050,
    debug=True
)
    
    """