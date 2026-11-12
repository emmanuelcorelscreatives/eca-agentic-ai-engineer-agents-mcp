"""Capture the genuine pinned Inspector UI; no model or external account access."""
import argparse
import json
import os
from pathlib import Path
import secrets
import signal
import socket
import subprocess
import sys
import time
import urllib.request
from playwright.sync_api import sync_playwright


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--chrome", required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    here = Path(__file__).resolve().parent
    config = args.output / "course-only-config.json"
    config.write_text(json.dumps({"mcpServers": {"academy-laboratory": {"type": "stdio", "command": sys.executable, "args": [str(here.parent / "server.py")]}}}))
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    token = secrets.token_urlsafe(32)
    env = dict(os.environ, HOST="127.0.0.1", CLIENT_PORT=str(port), MCP_SANDBOX_PORT="0", MCP_APP_ORIGIN_PORT="0", MCP_STORAGE_DIR=str(args.output / "isolated-storage"), MCP_INSPECTOR_SECRET_STORE="memory", MCP_INSPECTOR_API_TOKEN=token, BROWSER="none")
    log = open(args.output / "inspector-private.log", "w")
    os.chmod(args.output / "inspector-private.log", 0o600)
    command = ["node", str(here / "node_modules/@modelcontextprotocol/inspector/clients/launcher/build/index.js"), "--web", "--config", str(config)]
    process = subprocess.Popen(command, env=env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    result = {"state": "STARTED", "inspector": "2.15.0", "paid_calls": 0, "pid": process.pid}
    try:
        url = f"http://127.0.0.1:{port}"
        for _ in range(180):
            if process.poll() is not None:
                raise RuntimeError("Inspector exited before readiness; see private log")
            try:
                with urllib.request.urlopen(url + "/healthz", timeout=1) as response:
                    if response.status == 200:
                        break
            except OSError:
                time.sleep(.5)
        else:
            raise TimeoutError("Inspector readiness timed out")
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(executable_path=args.chrome, headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
            try:
                page = browser.new_page(viewport={"width": 1440, "height": 1000})
                page.goto(url, wait_until="networkidle")
                page.screenshot(path=str(args.output / "01-initial.png"))
                (args.output / "01-initial-dom.txt").write_text(page.locator("body").inner_text())
                result["initial_browser_pass"] = True
                buttons = page.get_by_role("button", name="Connect", exact=True)
                if buttons.count():
                    buttons.first.click()
                else:
                    server = page.get_by_text("academy-laboratory", exact=True)
                    if server.count():
                        server.first.click()
                    page.get_by_role("button", name="Connect", exact=True).first.click()
                page.wait_for_timeout(2500)
                (args.output / "02-connected-dom.txt").write_text(page.locator("body").inner_text())
                page.screenshot(path=str(args.output / "02-connected.png"))
                result["state"] = "BROWSER_CONNECTED_ATTEMPT_REQUIRES_DOM_CHECK"
            finally:
                browser.close()
    finally:
        if process.poll() is None:
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=8)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait(timeout=5)
        log.close()
        result["server_process_terminal"] = process.poll() is not None
        (args.output / "result.json").write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
