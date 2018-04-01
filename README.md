Change/fill in `js/main.js` and the HTML widgets in `index.html` for the GUI.
Change `relay_test.py` to send data over (`import relay; relay.send_data( ... )`).
Change `index.html`'s `function receive()` to do something with that data.

To run:

1. Launch `./relay.py`
2. Run a web server (e.g. `python3 -m http.server`) and browse to `http://localhost:8000/'.
3. Run your Python code that calls `relay.send_data()`.
