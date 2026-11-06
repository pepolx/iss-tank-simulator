"""Uruchom: python app.py, potem otwórz http://127.0.0.1:8050."""
import csv
import io
from dataclasses import replace

from dash import Dash, Input, Output, State, dcc, html
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from model import Parametry, symulacja, poziom_rownowagi

DEFAULT = Parametry()
KONTROLKI = [
    ("A", "Pole przekroju A [m²]", 0.5, 5, 0.1),
    ("beta", "Współczynnik wypływu β [m^(5/2)/s]", 0, 0.1, 0.001),
    ("Q_doplyw", "Dopływ Qd [m³/s]", 0, 0.15, 0.001),
    ("current_h", "Poziom początkowy h₀ [m]", 0, 5, 0.1),
]
IDS = [k[0] for k in KONTROLKI]


def parametry(wartosci):
    return replace(DEFAULT, **dict(zip(IDS, wartosci)))


def wykres(p, wynik):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        vertical_spacing=0.12, subplot_titles=("Poziom wody", "Dopływ i odpływ"))
    fig.add_trace(go.Scatter(x=wynik.t, y=wynik.h, name="h [m]", line_color="#2463eb"), row=1, col=1)
    fig.add_hline(y=p.h_max, line_dash="dot", line_color="#8893a5", row=1, col=1)
    h_eq = poziom_rownowagi(p)
    if h_eq is not None and 0 <= h_eq <= p.h_max:
        fig.add_hline(y=h_eq, line_dash="dash", line_color="#16a085", row=1, col=1)
    fig.add_trace(go.Scatter(x=[0, p.t_sim], y=[p.Q_doplyw]*2, name="Dopływ Qd", line_dash="dash"), row=2, col=1)
    fig.add_trace(go.Scatter(x=wynik.t, y=wynik.Q_odplyw, name="Odpływ Qo", line_color="#e88625"), row=2, col=1)
    if any(q > 1e-10 for q in wynik.Q_przelew):
        fig.add_trace(go.Scatter(x=wynik.t, y=wynik.Q_przelew, name="Przelew (średni w kroku)", line_color="#d64e62"), row=2, col=1)
    fig.update_yaxes(title_text="h [m]", range=[0, p.h_max*1.05], row=1, col=1)
    fig.update_yaxes(title_text="Q [m³/s]", rangemode="tozero", row=2, col=1)
    fig.update_xaxes(title_text="Czas [s]", row=2, col=1)
    fig.update_layout(template="plotly_white", height=640, hovermode="x unified",
                      margin=dict(l=55, r=25, t=55, b=40), legend=dict(orientation="h", y=1.12))
    return fig


def csv_wynikow(p):
    wynik = symulacja(p)
    plik = io.StringIO(newline="")
    writer = csv.writer(plik)
    writer.writerow(["t_s", "h_m", "h_cm", "Q_doplyw_m3_s", "Q_odplyw_m3_s", "Q_przelew_m3_s"])
    for t, h, qo, qp in zip(wynik.t, wynik.h, wynik.Q_odplyw, wynik.Q_przelew):
        writer.writerow([t, h, h*100, p.Q_doplyw, qo, qp])
    return plik.getvalue()


app = Dash(__name__, title="ISS · Symulacja zbiornika")
server = app.server
app.layout = html.Main([
    html.Header([html.P("INTELIGENTNE SYSTEMY STEROWANIA", className="eyebrow"),
                 html.H1("Zbiornik z odpływem swobodnym"),
                 html.P("Zmieniaj parametry i obserwuj poziom wody oraz przepływy. Dopływ jest stały w obrębie jednej symulacji.")]),
    html.Div([
        html.Aside([
            html.H2("Parametry"),
            *[html.Div([
                html.Label(label, htmlFor=nazwa),
                dcc.Slider(id=nazwa, min=lo, max=hi, step=step,
                           value=getattr(DEFAULT, nazwa), marks={lo: str(lo), hi: str(hi)},
                           tooltip={"placement": "bottom", "always_visible": True}, updatemode="mouseup")
            ], className="control") for nazwa, label, lo, hi, step in KONTROLKI],
            html.P("Tp = 0,1 s · czas = 3600 s · wysokość = 5 m", className="muted"),
            html.Button("Przywróć wartości początkowe", id="reset", n_clicks=0),
            html.Button("Pobierz wyniki CSV", id="eksport", n_clicks=0),
            dcc.Download(id="csv")
        ], className="panel"),
        html.Section([html.Div(id="metryki", className="metrics"),
                      dcc.Graph(id="wykres", config={"displaylogo": False, "responsive": True}),
                      html.P(id="stan", className="status")], className="panel results")
    ], className="layout"),
    html.Details([html.Summary("Model i interpretacja"),
        dcc.Markdown(r"""
$$h_{n+1}=h_n+\frac{T_p}{A}(Q_d-\beta\sqrt{h_n})$$

Bilans objętości obliczamy jawną metodą Eulera. `h` jest w metrach, `Q` w m³/s.
Poziom równowagi bez ograniczenia wysokością: $h_*=(Q_d/\beta)^2$ dla $\beta>0$.
Powyżej równowagi odpływ przewyższa dopływ i poziom maleje; poniżej rośnie.
Pole przekroju A wpływa na szybkość zmian, a nie na poziom równowagi.

Poziom ograniczamy do 0–5 m. Nadmiar przy górnej granicy traktujemy jako przelew.
Przy opróżnianiu dolna granica jest zabezpieczeniem numerycznym: Euler może
przewidzieć ujemny poziom w ostatnim kroku. Qo to wartość ze wzoru na początku
kroku, a nie dokładny średni przepływ podczas tego kroku.
Model nie zawiera regulatora P/PID ani dynamiki zaworu.
""", mathjax=True)
    ], className="panel explanation")
])


@app.callback(Output("wykres", "figure"), Output("metryki", "children"),
              Output("stan", "children"), *[Input(nazwa, "value") for nazwa in IDS])
def aktualizuj(*wartosci):
    p = parametry(wartosci)
    wynik = symulacja(p)
    h_eq = poziom_rownowagi(p)
    metryki = [html.Div([html.Small(label), html.Strong(value)]) for label, value in [
        ("Najwyższy poziom", f"{max(wynik.h)*100:.2f} cm"),
        ("Poziom końcowy", f"{wynik.h[-1]*100:.2f} cm"),
        ("Liczba wyników", str(len(wynik.h)))]]
    if h_eq is None:
        stan = "β = 0: brak odpływu. Przy dodatnim dopływie zbiornik napełnia się do przelewu; przy zerowym poziom pozostaje stały."
    elif h_eq > p.h_max:
        stan = f"Równowaga bez ograniczeń: {h_eq:.3f} m — powyżej wysokości zbiornika. Po osiągnięciu 5 m nadmiar przelewa się."
    else:
        stan = f"Teoretyczny poziom równowagi: {h_eq:.4f} m ({h_eq*100:.2f} cm). Linia przerywana wskazuje tę wartość."
    return wykres(p, wynik), metryki, stan


@app.callback(*[Output(nazwa, "value") for nazwa in IDS], Input("reset", "n_clicks"), prevent_initial_call=True)
def reset(n_clicks):
    return [getattr(DEFAULT, nazwa) for nazwa in IDS]


@app.callback(Output("csv", "data"), Input("eksport", "n_clicks"),
              *[State(nazwa, "value") for nazwa in IDS], prevent_initial_call=True)
def eksport(n_clicks, *wartosci):
    return dcc.send_string(csv_wynikow(parametry(wartosci)), "wyniki_zbiornika.csv")


if __name__ == "__main__":
    print("Otwórz http://127.0.0.1:8050 w przeglądarce. Zatrzymanie: Ctrl+C.")
    app.run(debug=False, host="127.0.0.1", port=8050)
