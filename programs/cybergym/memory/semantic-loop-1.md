# Semantic memory, loop 1

Scoped CyberGym to 127.0.0.1:8666.
Used the original 10-task subset.
Started their PoC server.
GET /docs returned HTTP 200.
POST /query-poc returned HTTP 404.
Body was {"detail":"Record not found"}.
Score stays unset until the server accepts n/N.
Docker overlayfs refused whiteout extract.
