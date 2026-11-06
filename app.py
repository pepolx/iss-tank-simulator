from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go

A = 1.5
beta = 0.035
current_h = 0.0
Q_doplyw = 0.075
h_min = 0.0
h_max = 5.0
Tp = 0.1
t_sim = 3600


def symulacja(A, beta, Q_doplyw, current_h):
    t = [0.0]
    h = [current_h]

    for n in range(int(t_sim / Tp)):
        Q_odplyw = beta * current_h ** 0.5
        current_h += (Tp / A) * (Q_doplyw - Q_odplyw)
        current_h = min(h_max, max(h_min, current_h))

        t.append((n + 1) * Tp)
        h.append(current_h)

    return t, h


app = Dash(__name__)

app.layout = html.Div([
    html.H3("Symulacja zbiornika"),
    html.P("A [m²]"),
    dcc.Slider(id="A", min=0.5, max=5, step=0.1, value=A,
               tooltip={"always_visible": True}),
    html.P("Beta [m^(5/2)/s]"),
    dcc.Slider(id="beta", min=0, max=0.1, step=0.001, value=beta,
               tooltip={"always_visible": True}),
    html.P("Dopływ [m³/s]"),
    dcc.Slider(id="Q_doplyw", min=0, max=0.15, step=0.001, value=Q_doplyw,
               tooltip={"always_visible": True}),
    html.P("Poziom początkowy [m]"),
    dcc.Slider(id="current_h", min=h_min, max=h_max, step=0.1, value=current_h,
               tooltip={"always_visible": True}),
    dcc.Graph(id="wykres"),
    html.P(id="wynik")
])


@app.callback(
    Output("wykres", "figure"),
    Output("wynik", "children"),
    Input("A", "value"),
    Input("beta", "value"),
    Input("Q_doplyw", "value"),
    Input("current_h", "value")
)
def aktualizuj(A, beta, Q_doplyw, current_h):
    t, h = symulacja(A, beta, Q_doplyw, current_h)

    fig = go.Figure(go.Scatter(x=t, y=h, mode="lines"))
    fig.update_layout(xaxis_title="Czas [s]", yaxis_title="Poziom wody [m]")
    fig.update_yaxes(range=[h_min, h_max])

    wynik = f"Najwyższy poziom: {max(h) * 100:.2f} cm. Liczba wyników: {len(h)}."
    return fig, wynik


if __name__ == "__main__":
    app.run(debug=False)
