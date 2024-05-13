import sys
import json
import time

header = f"""# Anicca AOSC
This is a small utility to run `aosc-findupdate` regularly by GitHub Actions.
## Result
![Relative date](https://img.shields.io/date/{int(time.time())}?label=Updated)"""

if __name__ == "__main__":
    print(header)
    print("| Package | Repo Version | New Version | Category | Warnings |")
    print("|---------|--------------|-------------|------|----------|")

    table = json.loads(sys.stdin.read())

    for row in sorted(table, key=lambda x: x["name"]):
        row["before"] = row["before"].replace("+", "<br>+")
        row["warnings"] = "<br>".join(row["warnings"])
        row["path"] = row["path"].split('/')[0]

        print("|" + "|".join(row.values()) + "|")
