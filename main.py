import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Dict, List

from infrai_client import InfraiClient


def choose_follow_up(results: List[Dict[str, object]]) -> Dict[str, object]:
    """Turn ranked legal matters into the next storefront-ops style work queue item."""
    if not results:
        return {"action": "review", "matter": None}
    first = results[0]
    metadata = first.get("metadata", {})
    if metadata.get("deadline_days", 99) <= 3:
        return {"action": "deadline_follow_up", "matter": metadata.get("matter_id")}
    if metadata.get("signed", False):
        return {"action": "deliver_signed_document", "matter": metadata.get("matter_id")}
    return {"action": "matter_intake", "matter": metadata.get("matter_id")}


class SearchHandler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        if self.path != "/search":
            self.send_error(404)
            return
        size = int(self.headers.get("Content-Length", "0"))
        body = json.loads(self.rfile.read(size))
        client = InfraiClient()
        # The caller supplies a precomputed embedding, as required by vector.query.
        envelope = client.query(body["collection"], body["embedding"], body.get("top_k", 5))
        decision = choose_follow_up(envelope["data"].get("results", []))
        payload = json.dumps({"ok": True, "data": {"decision": decision}}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(payload)


if __name__ == "__main__":
    HTTPServer(("127.0.0.1", 8000), SearchHandler).serve_forever()
