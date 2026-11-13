# Registry operations

```sh
python3 /absolute/skill/path/scripts/ports.py list
python3 /absolute/skill/path/scripts/ports.py allocate --project /absolute/project --service web
python3 /absolute/skill/path/scripts/ports.py allocate --project /absolute/project --service api --port 3201
python3 /absolute/skill/path/scripts/ports.py check
python3 /absolute/skill/path/scripts/ports.py release --project /absolute/project --service api
```

Allocation reuses an existing assignment, otherwise selects a port from 3000–9999 unless a different range or exact port is requested. SQLite transactions serialize cooperating allocations, including separate Codex chats. Reservations are conservative across host addresses for each transport. TCP and UDP have separate assignments; reserve both explicitly when necessary. The helper probes IPv4 and supported IPv6 wildcard binds but cannot hold the socket until the application starts.

An occupied requested port is rejected. Use `--adopt-occupied --port NUMBER` only after verifying that its listener/container belongs to this exact project and service. Never use adoption to bypass another registry assignment. A reused occupied assignment remains unchanged: `bind_available: false` may indicate the correct running app, not a conflict. Identify ownership through scoped listener/process or Docker inspection before deciding. Inspection reports availability, not process ownership or application health.
