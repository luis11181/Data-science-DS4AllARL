from index import server
from waitress import serve

serve(server, host="0.0.0.0", port=80)