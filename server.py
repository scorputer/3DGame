"""
Cross-Platform Game Host & REST/Co-Evolution State Bridge.

Junior Dev Note:
----------------
This lightweight Python server allows you to run the 3D Evolution Game inside
a Docker container (`docker compose up --build`) and play it from any browser on
Windows, Android, iOS, or Linux at `http://localhost:8080`.
It also exposes a `/api/health` and `/api/simulate` endpoint backed by `luca_engine`.
"""

import argparse
import json
from http.server import SimpleHTTPRequestHandler, HTTPServer
from pathlib import Path
from src.luca_engine.logger import get_game_logger, MEMORY_HANDLER
from src.luca_engine.world import WorldSimulation

logger = get_game_logger("luca_engine.server")
WORLD = WorldSimulation()


class GameRequestHandler(SimpleHTTPRequestHandler):
    """Serves the 3D WebGL client and JSON simulation endpoints."""

    def do_GET(self) -> None:
        """Handle GET requests for the game UI and health/audit endpoints."""
        if self.path == "/api/health":
            payload = {
                "status": "ok",
                "epoch_mya": WORLD.epoch_age_mya,
                "biome": WORLD.current_biome_id,
                "recent_logs": MEMORY_HANDLER.records[-10:],
            }
            self._send_json(payload)
            return

        if self.path in ("/", "/index.html"):
            self.path = "/web_client/luca_3d_evolution.html"
        return super().do_GET()

    def _send_json(self, data: dict) -> None:
        """Serialize dictionary as UTF-8 JSON response."""
        raw = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)


def main() -> None:
    """Parse CLI arguments and start the HTTP server."""
    parser = argparse.ArgumentParser(description="LUCA 3D Evolution Server")
    parser.add_argument("--port", type=int, default=8080, help="Port to listen on")
    args = parser.parse_args()

    root_dir = Path(__file__).resolve().parent
    logger.info("Serving LUCA 3D Evolution from %s on port %d", root_dir, args.port)
    server = HTTPServer(("0.0.0.0", args.port), GameRequestHandler)
    server.serve_forever()


if __name__ == "__main__":
    main()
