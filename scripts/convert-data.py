from pathlib import Path
from subprocess import check_output
import json
from argparse import ArgumentParser


def get_timestamp_git(abbs_path: str, pkg_path: str) -> int:
    cmd = ["git", "-P", "log", "-1", "--format='%ct'", "--"]
    output = check_output(cmd + [pkg_path], cwd=abbs_path)
    return int(output.decode().strip("'\n"))


def get_timestamps_before_msg(abbs_path: Path, pkg_names: list[str]) -> dict[str, int]:
    cmd = ["git", "-P", "log", "--format='%ct: %s'"]
    commit_logs = check_output(cmd, cwd=abbs_path).decode().split("\n")
    pkg_times = {}

    for log in commit_logs:
        try:
            timestamp, pkg_name, msg = log.strip("'").split(": ", maxsplit=2)
        except ValueError:
            continue
        if pkg_name in pkg_names and ("update to" in msg or "new," in msg):
            pkg_names.remove(pkg_name)
            pkg_times[pkg_name] = int(timestamp)

    return pkg_times


def convert(abbs_path: Path, pkgsupdate: list[dict]) -> list[list]:
    anicca_data_keys = [
        "name",
        "before",
        "after",
        "path",
        "before_ts",
        # "after_ts",
        # "interval",
        "warnings",
    ]

    # Get before_ts
    pkg_not_found_in_msg = []
    pkg_times = get_timestamps_before_msg(
        abbs_path, [pkg["name"] for pkg in pkgsupdate]
    )
    for pkg in pkgsupdate:
        try:
            pkg["before_ts"] = pkg_times[pkg["name"]]
        except KeyError:
            pkg["before_ts"] = get_timestamp_git(str(abbs_path), pkg["path"])
            pkg_not_found_in_msg.append(pkg)

    # Show packages not found in commit message
    print(f"Pkgs not found in msg: {len(pkg_not_found_in_msg)} / {len(pkgsupdate)}")
    for pkg in sorted(pkg_not_found_in_msg, key=lambda x: x["name"]):
        print(pkg["name"])

    # Remove package name from path
    for pkg in pkgsupdate:
        pkg["path"] = "/".join(pkg["path"].split("/")[:-1])

    anicca_data = []
    for pkg in pkgsupdate:
        anicca_data.append([pkg[key] for key in anicca_data_keys])
    return anicca_data


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "-i", "--input", default="pkgsupdate.json", help="Input file (pkgsupdate)"
    )
    parser.add_argument(
        "-o", "--output", default="anicca-data.json", help="Output file (anicca-data)"
    )
    parser.add_argument(
        "-p", "--abbs-path", default="aosc-os-abbs", help="Path to aosc-os-abbs"
    )
    args = parser.parse_args()

    with open(args.input) as f:
        pkgsupdate = json.load(f)

    converted = convert(args.abbs_path, pkgsupdate)
    with open(args.output, "w") as f:
        f.write(
            "[\n"
            + ",\n".join([json.dumps(row, separators=(",", ":")) for row in converted])
            + "\n]"
        )  # For better git history
