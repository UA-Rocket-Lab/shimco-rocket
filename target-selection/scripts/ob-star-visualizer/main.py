from layout import app, default_layout
from callbacks import register_callbacks

app.layout = default_layout()

register_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True)