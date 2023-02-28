# Uruchomienie lokalnie
1. `pip install -r requirements.txt`
1. W osobnych terminalach `python3 src/server/server.py`,  `python3 src/view.py`

# Docker
1. `docker compose up -d`
1. `docker exec -it <db_container> sh -c "mysql < db.sql"`
1. `docker exec -it <client_container >python3 src/view.py`

Hasła do obu kont secret
Używa linków symbolicznych żeby udostępnić folder common w tests i w innych
