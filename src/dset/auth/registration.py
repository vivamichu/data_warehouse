import json

from dset.cache import licenses_file


def is_accepted(name: str) -> bool:
    p = licenses_file()
    if not p.exists():
        return False
    return name in json.loads(p.read_text()).get("accepted", [])


def accept(name: str) -> None:
    p = licenses_file()
    data = json.loads(p.read_text()) if p.exists() else {"accepted": []}
    if name not in data["accepted"]:
        data["accepted"].append(name)
    p.write_text(json.dumps(data, indent=2))


def prompt_and_accept(
    name: str, eula_url: str, message: str, auto: bool = False
) -> bool:
    if is_accepted(name):
        return True
    print(f"\n'{name}' requires accepting a license.")
    if eula_url:
        print(f"  EULA URL: {eula_url}")
    if message:
        print(f"  {message.strip()}")
    if auto:
        accept(name)
        return True
    answer = input("Have you read and accepted the terms? [y/N]: ").strip().lower()
    if answer == "y":
        accept(name)
        return True
    return False
