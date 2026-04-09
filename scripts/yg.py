#!/usr/bin/env python3
"""Yougile API CLI — project management, tasks, boards, columns.

Usage:
    yg.py <tool> '{"key": "value"}'
    yg.py <tool> - <<'ARGS'
    {"key": "value"}
    ARGS
    yg.py setup              # Interactive onboarding
"""

import json
import os
import platform
import subprocess
import sys
import urllib.error
import urllib.request

BASE = "https://yougile.com/api-v2"
KEYCHAIN_NAME = "yougile-api-key"


# ━━ Credential Storage (cross-platform) ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _is_macos():
    return platform.system() == "Darwin"


def _is_windows():
    return platform.system() == "Windows"


def get_stored_key(name: str) -> str | None:
    """Get secret from OS credential store or env var."""
    # 1. Environment variable (works everywhere)
    env_key = name.upper().replace("-", "_")
    val = os.environ.get(env_key)
    if val:
        return val

    # 2. macOS Keychain
    if _is_macos():
        try:
            return subprocess.check_output(
                ["security", "find-generic-password", "-s", name, "-w"],
                stderr=subprocess.DEVNULL,
            ).decode().strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

    # 3. Windows Credential Manager (via cmdkey + PowerShell)
    if _is_windows():
        try:
            ps = (
                f'(Get-StoredCredential -Target "{name}").GetNetworkCredential().Password'
            )
            return subprocess.check_output(
                ["powershell", "-Command", ps],
                stderr=subprocess.DEVNULL,
            ).decode().strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Fallback: read from cmdkey-compatible file
            pass

    return None


def store_key(name: str, value: str):
    """Store secret in OS credential store."""
    if _is_macos():
        # Delete existing (ignore errors)
        subprocess.run(
            ["security", "delete-generic-password", "-s", name],
            capture_output=True,
        )
        subprocess.run(
            [
                "security", "add-generic-password",
                "-a", os.environ.get("USER", "yougile"),
                "-s", name, "-w", value,
            ],
            check=True,
        )
        return True

    if _is_windows():
        try:
            subprocess.run(
                ["cmdkey", f"/generic:{name}", "/user:yougile", f"/pass:{value}"],
                check=True, capture_output=True,
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

    return False


def get_token() -> str:
    """Get API key from storage."""
    token = get_stored_key(KEYCHAIN_NAME)
    if not token:
        fail(
            "No API key found. Run setup first:\n"
            "  python3 scripts/yg.py setup\n\n"
            "Or set environment variable:\n"
            f"  export YOUGILE_API_KEY='your-key'"
        )
    return token


# ━━ API ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def api(method: str, path: str, body=None, token=None):
    """Make API request."""
    url = f"{BASE}{path}" if path.startswith("/") else f"{BASE}/{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        body_text = e.read().decode()
        fail(f"HTTP {e.code}: {body_text[:500]}")


def fail(msg):
    print(json.dumps({"error": msg}), file=sys.stderr)
    sys.exit(1)


# ━━ Setup / Onboarding ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def setup(_=None, a=None):
    """Interactive onboarding: login → pick company → create & store API key."""
    print("=== Yougile API Setup ===\n")

    # Check if already configured
    existing = get_stored_key(KEYCHAIN_NAME)
    if existing:
        print("API key already configured. Testing...")
        try:
            result = api("GET", "/projects?limit=1", token=existing)
            count = result.get("paging", {}).get("count", "?")
            print(f"OK! Connected. {count} project(s) accessible.")
            print("\nTo reconfigure, delete the key first:")
            if _is_macos():
                print(f"  security delete-generic-password -s {KEYCHAIN_NAME}")
            elif _is_windows():
                print(f"  cmdkey /delete:{KEYCHAIN_NAME}")
            else:
                print(f"  unset YOUGILE_API_KEY")
            return
        except SystemExit:
            print("Existing key is invalid. Proceeding with setup...\n")

    # Get credentials
    if a and "login" in a and "password" in a:
        login, password = a["login"], a["password"]
    else:
        login = input("Yougile email: ").strip()
        password = input("Yougile password: ").strip()

    if not login or not password:
        print("ERROR: Email and password are required.")
        return

    # Get companies
    print(f"\nFetching companies for {login}...")
    try:
        result = api("POST", "/auth/companies", {"login": login, "password": password})
    except SystemExit:
        print("\nFailed. Check your email/password.")
        print("If you registered via Google, set a password in Yougile settings first.")
        return

    companies = result.get("content", [])
    if not companies:
        print("No companies found.")
        return

    # Pick company
    if len(companies) == 1:
        company = companies[0]
        print(f"Found company: {company['name']}")
    else:
        print(f"\nFound {len(companies)} companies:")
        for i, c in enumerate(companies):
            admin = " (admin)" if c.get("isAdmin") else ""
            print(f"  [{i + 1}] {c['name']}{admin}")

        if a and "companyIndex" in a:
            idx = int(a["companyIndex"]) - 1
        else:
            choice = input(f"\nSelect company [1-{len(companies)}]: ").strip()
            idx = int(choice) - 1

        if idx < 0 or idx >= len(companies):
            print("Invalid selection.")
            return
        company = companies[idx]

    # Create API key
    print(f"\nCreating API key for '{company['name']}'...")
    result = api("POST", "/auth/keys", {
        "login": login, "password": password, "companyId": company["id"],
    })
    key = result.get("key")
    if not key:
        print(f"ERROR: Unexpected response: {result}")
        return

    # Store key
    stored = store_key(KEYCHAIN_NAME, key)
    if stored:
        store_name = "Keychain" if _is_macos() else "Credential Manager" if _is_windows() else "storage"
        print(f"API key saved to {store_name}!")
    else:
        print(f"\nCould not auto-store key. Set it manually:")
        print(f"  export YOUGILE_API_KEY='{key}'")
        print(f"\nOr add to your shell profile (~/.bashrc, ~/.zshrc):")
        print(f"  echo 'export YOUGILE_API_KEY=\"{key}\"' >> ~/.zshrc")

    # Verify
    print("\nVerifying...")
    projects = api("GET", "/projects", token=key)
    count = projects.get("paging", {}).get("count", 0)
    print(f"Connected to '{company['name']}' — {count} project(s) found.")
    print("\n=== Setup complete! ===")


# ━━ Auth ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def auth_companies(_, a):
    """Get companies list (requires login+password)."""
    return api("POST", "/auth/companies", {"login": a["login"], "password": a["password"]})


def auth_create_key(_, a):
    """Create API key (requires login+password+companyId)."""
    return api("POST", "/auth/keys", {
        "login": a["login"], "password": a["password"], "companyId": a["companyId"],
    })


def auth_list_keys(_, a):
    """List API keys."""
    return api("POST", "/auth/keys/get", {
        "login": a["login"], "password": a["password"],
        **({"companyId": a["companyId"]} if "companyId" in a else {}),
    })


# ━━ Projects ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def projects_list(token, a):
    """List projects."""
    q = _query(a, "includeDeleted", "limit", "offset", "title")
    return api("GET", f"/projects{q}", token=token)


def projects_get(token, a):
    """Get project by ID."""
    return api("GET", f"/projects/{a['id']}", token=token)


def projects_create(token, a):
    """Create project."""
    body = {"title": a["title"]}
    if "users" in a:
        body["users"] = a["users"]
    return api("POST", "/projects", body, token)


def projects_update(token, a):
    """Update project."""
    pid = a.pop("id")
    return api("PUT", f"/projects/{pid}", a, token)


# ━━ Boards ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def boards_list(token, a):
    """List boards."""
    q = _query(a, "includeDeleted", "limit", "offset", "title", "projectId")
    return api("GET", f"/boards{q}", token=token)


def boards_get(token, a):
    """Get board by ID."""
    return api("GET", f"/boards/{a['id']}", token=token)


def boards_create(token, a):
    """Create board."""
    body = {"title": a["title"], "projectId": a["projectId"]}
    if "stickers" in a:
        body["stickers"] = a["stickers"]
    return api("POST", "/boards", body, token)


def boards_update(token, a):
    """Update board."""
    bid = a.pop("id")
    return api("PUT", f"/boards/{bid}", a, token)


# ━━ Columns ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def columns_list(token, a):
    """List columns."""
    q = _query(a, "includeDeleted", "limit", "offset", "title", "boardId")
    return api("GET", f"/columns{q}", token=token)


def columns_get(token, a):
    """Get column by ID."""
    return api("GET", f"/columns/{a['id']}", token=token)


def columns_create(token, a):
    """Create column."""
    body = {"title": a["title"], "boardId": a["boardId"]}
    if "color" in a:
        body["color"] = a["color"]
    return api("POST", "/columns", body, token)


def columns_update(token, a):
    """Update column."""
    cid = a.pop("id")
    return api("PUT", f"/columns/{cid}", a, token)


# ━━ Tasks ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def tasks_list(token, a):
    """List tasks (reverse chronological)."""
    q = _query(a, "includeDeleted", "limit", "offset", "title", "columnId",
               "assignedTo", "stickerId", "stickerStateId")
    return api("GET", f"/tasks{q}", token=token)


def tasks_list_chrono(token, a):
    """List tasks (chronological order)."""
    q = _query(a, "includeDeleted", "limit", "offset", "title", "columnId",
               "assignedTo", "stickerId", "stickerStateId")
    return api("GET", f"/task-list{q}", token=token)


def tasks_get(token, a):
    """Get task by ID."""
    return api("GET", f"/tasks/{a['id']}", token=token)


def tasks_create(token, a):
    """Create task. Required: title. Optional: columnId, description, assigned, deadline, etc."""
    return api("POST", "/tasks", a, token)


def tasks_update(token, a):
    """Update task."""
    tid = a.pop("id")
    return api("PUT", f"/tasks/{tid}", a, token)


# ━━ Users ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def users_list(token, a):
    """List users."""
    q = _query(a, "limit", "offset", "email", "projectId")
    return api("GET", f"/users{q}", token=token)


def users_get(token, a):
    """Get user by ID."""
    return api("GET", f"/users/{a['id']}", token=token)


# ━━ Chat Messages ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def chat_messages(token, a):
    """Get chat messages for a task or group chat."""
    chat_id = a["chatId"]
    q = _query(a, "includeDeleted", "limit", "offset", "fromUserId", "text", "label", "since")
    return api("GET", f"/chats/{chat_id}/messages{q}", token=token)


def chat_send(token, a):
    """Send message to chat."""
    chat_id = a.pop("chatId")
    return api("POST", f"/chats/{chat_id}/messages", a, token)


# ━━ Webhooks ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def webhooks_list(token, a):
    """List webhooks."""
    q = _query(a, "includeDeleted")
    return api("GET", f"/webhooks{q}", token=token)


def webhooks_create(token, a):
    """Create webhook."""
    return api("POST", "/webhooks", a, token)


def webhooks_update(token, a):
    """Update webhook."""
    wid = a.pop("id")
    return api("PUT", f"/webhooks/{wid}", a, token)


# ━━ Helpers ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _query(a, *keys):
    """Build query string from args."""
    params = []
    for k in keys:
        if k in a:
            params.append(f"{k}={urllib.request.quote(str(a[k]))}")
    return f"?{'&'.join(params)}" if params else ""


# ━━ Tool Registry ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TOOLS = {
    "setup": setup,
    # Auth (no token needed)
    "auth_companies": auth_companies,
    "auth_create_key": auth_create_key,
    "auth_list_keys": auth_list_keys,
    # Projects
    "projects_list": projects_list,
    "projects_get": projects_get,
    "projects_create": projects_create,
    "projects_update": projects_update,
    # Boards
    "boards_list": boards_list,
    "boards_get": boards_get,
    "boards_create": boards_create,
    "boards_update": boards_update,
    # Columns
    "columns_list": columns_list,
    "columns_get": columns_get,
    "columns_create": columns_create,
    "columns_update": columns_update,
    # Tasks
    "tasks_list": tasks_list,
    "tasks_list_chrono": tasks_list_chrono,
    "tasks_get": tasks_get,
    "tasks_create": tasks_create,
    "tasks_update": tasks_update,
    # Users
    "users_list": users_list,
    "users_get": users_get,
    # Chat
    "chat_messages": chat_messages,
    "chat_send": chat_send,
    # Webhooks
    "webhooks_list": webhooks_list,
    "webhooks_create": webhooks_create,
    "webhooks_update": webhooks_update,
}

NO_TOKEN_TOOLS = {"setup", "auth_companies", "auth_create_key", "auth_list_keys"}


def main():
    if len(sys.argv) < 2 or sys.argv[1] == "--help":
        print("Yougile API CLI\n")
        print("Usage: yg.py <tool> [json_args]\n")
        print("Setup:  yg.py setup\n")
        print(f"Tools: {', '.join(sorted(TOOLS))}")
        sys.exit(0)

    tool = sys.argv[1]

    if tool not in TOOLS:
        fail(f"Unknown tool '{tool}'. Available: {', '.join(sorted(TOOLS))}")

    # Parse args
    args = {}
    if len(sys.argv) > 2:
        raw = sys.argv[2]
        if raw == "-":
            raw = sys.stdin.read()
        args = json.loads(raw)

    # No-token tools
    if tool in NO_TOKEN_TOOLS:
        result = TOOLS[tool](None, args)
    else:
        token = get_token()
        result = TOOLS[tool](token, args)

    if result is not None:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
