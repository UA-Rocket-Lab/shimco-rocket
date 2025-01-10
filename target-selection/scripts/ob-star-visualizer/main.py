from layout import app, default_layout, args
from callbacks import register_callbacks
import os

app.layout = default_layout()
register_callbacks(app)

if __name__ == '__main__':

    if args.local:
        app.run_server(debug=True)
    else:
        port = int(os.environ.get("PORT", 8050))
        app.run_server(host='0.0.0.0', port=port, debug=True)