from layout import app, default_layout
from callbacks import register_callbacks
import os

app.layout = default_layout()

register_callbacks(app)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))
    app.run_server(host='0.0.0.0', port=port, debug=True)
    # app.run_server(debug=True)