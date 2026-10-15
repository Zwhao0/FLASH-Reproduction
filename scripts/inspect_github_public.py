#!/usr/bin/env python3
"""Read only public settings for the sole authorized repository; no credentials."""
import json
import urllib.error
import urllib.request

BASE = "https://api.github.com/repos/Zwhao0/FLASH-Reproduction"


def main():
    failures = 0
    for endpoint in ("", "/branches/main", "/branches/main/protection", "/rulesets"):
        request = urllib.request.Request(BASE + endpoint, headers={
            "Accept": "application/vnd.github+json", "User-Agent": "FLASH-P0-read-only",
        })
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                data = json.load(response)
                if not endpoint:
                    result = {k: data.get(k) for k in (
                        "full_name", "visibility", "default_branch", "archived")}
                elif endpoint == "/branches/main":
                    result = {"head": data["commit"]["sha"],
                              "protected": data.get("protected"),
                              "protection": data.get("protection")}
                elif endpoint == "/rulesets":
                    result = [{k: rule.get(k) for k in (
                        "id", "name", "target", "enforcement")} for rule in data]
                else:
                    result = {"readable": True}
                print(json.dumps({"endpoint": endpoint or "/", "http": response.status,
                                  "result": result}, sort_keys=True))
        except urllib.error.HTTPError as error:
            print(json.dumps({"endpoint": endpoint, "http": error.code,
                              "result": "INCONCLUSIVE: public API could not read this setting"}))
            if endpoint != "/branches/main/protection" or error.code not in (401, 403, 404):
                failures += 1
        except (urllib.error.URLError, TimeoutError, ValueError, KeyError):
            print(json.dumps({"endpoint": endpoint, "result": "FAIL: request or response"}))
            failures += 1
    print("No permission mutations or permission negative tests performed.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
