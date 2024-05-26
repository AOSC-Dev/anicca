from pathlib import Path
from multiprocessing import Pool
from subprocess import check_output
import json
from argparse import ArgumentParser

abbs_path = Path("aosc-os-abbs")
git_cmd = "git -P log -1 --format='%ct' -- ".split()


def get_timestamp_git(abbs_path: str, pkg_path: str) -> int:
    output = check_output(git_cmd + [pkg_path], cwd=abbs_path)
    return int(output.decode().strip("'\n"))


def get_timestamps_before(abbs_path: Path, pkg_paths: list[str]) -> list[int]:
    base_path = str(abbs_path.resolve())
    with Pool() as p:
        result = p.starmap(
            get_timestamp_git, [(base_path, pkg_path) for pkg_path in pkg_paths]
        )
    return result  # TODO: exception handling


def convert(pkgsupdate: list[dict]):
    final_keys = [
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
    for i, before_ts in enumerate(
        get_timestamps_before(abbs_path, [pkg["path"] for pkg in pkgsupdate])
    ):
        pkgsupdate[i]["before_ts"] = before_ts

    # Remove package name from path
    for pkg in pkgsupdate:
        pkg["path"] = "/".join(pkg["path"].split("/")[:-1])

    anicca_data = []
    for pkg in pkgsupdate:
        anicca_data.append([pkg[key] for key in final_keys])
    return anicca_data


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "-i", "--input", default="pkgsupdate.json", help="Input file (pkgsupdate)"
    )
    parser.add_argument(
        "-o", "--output", default="anicca-data.json", help="Output file (anicca-data)"
    )
    args = parser.parse_args()

    with open(args.input) as f:
        pkgsupdate = json.load(f)

    converted = convert(pkgsupdate)
    with open(args.output, "w") as f:
        f.write(
            "[\n"
            + ",\n".join([json.dumps(row, separators=(",", ":")) for row in converted])
            + "\n]"
        )   # For better git history
