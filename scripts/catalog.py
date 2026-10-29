#!/usr/bin/env python3
"""Read the bundled design catalog without installing or rendering anything."""
import argparse
import json
import sys
from _contracts import catalog, KINDS


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kind", choices=KINDS, required=True)
    parser.add_argument("action", choices=["list", "get"])
    parser.add_argument("id", nargs="?")
    parser.add_argument("--query", default="")
    parser.add_argument("--scenario")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--catalog-dir", help=argparse.SUPPRESS)
    parser.add_argument("--style-root", action="append", default=None, help="additional style package collection")
    args = parser.parse_args()
    try:
        entries = catalog(args.kind, args.catalog_dir, style_roots=args.style_root)
        if args.action == "get":
            if args.kind in {"style", "recipe"} and args.id not in entries and isinstance(args.id, str):
                matches = [k for k,v in entries.items() if args.id.strip().casefold() in {s.casefold() for s in [v['name'], *v.get('aliases',[])]}]
                if len(matches) == 1:
                    args.id = matches[0]
                elif len(matches) > 1:
                    raise ValueError("ambiguous name; use an ID: " + ", ".join(matches))
            if args.id not in entries:
                raise ValueError("unknown or missing ID: " + str(args.id))
            result = dict(schema_version=1, kind=args.kind, item=entries[args.id])
        else:
            if args.id:
                raise ValueError("list does not accept an ID")
            allowed = None
            if args.scenario:
                scenarios = catalog("scenario", args.catalog_dir)
                if args.scenario not in scenarios:
                    raise ValueError("unknown scenario: " + args.scenario)
                scenario = scenarios[args.scenario]
                allowed = {args.scenario} if args.kind == "scenario" else set(scenario.get(args.kind + "_ids", []))
            query = args.query.casefold()
            items = [item for key, item in entries.items()
                     if (allowed is None or key in allowed or args.kind == "style" and args.scenario in item.get("scenario_ids", []))
                     and query in json.dumps(item, ensure_ascii=False).casefold()]
            result = dict(schema_version=1, kind=args.kind, items=items)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            for item in ([result["item"]] if "item" in result else result["items"]):
                print(f"{item['id']}\t{item.get('name', '')}\t{item.get('intent', '')}")
                if args.action == "get":
                    for key, value in item.items():
                        if key not in ["id", "name", "intent"]:
                            print(key + ": " + json.dumps(value, ensure_ascii=False))
        return 0
    except (OSError, ValueError, KeyError) as exc:
        print(json.dumps(dict(schema_version=1, status="failed", error=str(exc)), ensure_ascii=False))
        return 2


if __name__ == "__main__":
    sys.exit(main())
