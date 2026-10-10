"""Build the public apps.json from a dump of the register's "apps" collection.

Usage: python scripts/build_public.py <dump.json> apps.json

The dump is a JSON array of app records (the "data" objects from the register).
Only apps marked "In programme", "Shortlist" or "Not recommended" are published, and only public fields are kept.
"""
import json
import sys
from datetime import datetime, timezone

PUBLIC_FIELDS = ["name", "category", "url", "whatItDoes", "why", "price", "nz"]
TIERS = {"In programme": "pick", "Shortlist": "radar", "Not recommended": "avoid"}


def build(records):
    apps = []
    for r in records:
        tier = TIERS.get(r.get("programme") or "")
        if not tier:
            continue
        app = {k: r.get(k, "") for k in PUBLIC_FIELDS}
        app["tier"] = tier
        apps.append(app)
    order = {"pick": 0, "radar": 1, "avoid": 2}
    apps.sort(key=lambda a: (order[a["tier"]], a["category"], a["name"]))
    return {"updatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"), "apps": apps}


def main():
    src, dest = sys.argv[1], sys.argv[2]
    with open(src) as f:
        records = json.load(f)
    out = build(records)
    # Leave the file untouched when the published list hasn't changed, so the site isn't redeployed for nothing.
    try:
        with open(dest) as f:
            if json.load(f).get("apps") == out["apps"]:
                print("unchanged")
                return
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    with open(dest, "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"wrote {len(out['apps'])} apps")


if __name__ == "__main__":
    main()
