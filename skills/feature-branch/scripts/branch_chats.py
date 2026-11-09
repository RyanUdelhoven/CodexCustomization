#!/usr/bin/env python3
"""Record branch/chat participation in shared local Git metadata. Never archive chats."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import uuid


def git(repo, *args):
    return subprocess.check_output(["git", "-C", repo, *args], text=True).strip()


def validate_record(record):
    def identity(value):
        return (isinstance(value, dict) and value.get("source") in ("codex", "chatgpt")
                and isinstance(value.get("hostId"), str)
                and isinstance(value.get("threadId"), str) and bool(value["threadId"])
                and (value["source"] != "chatgpt" or not value["hostId"]))
    if not isinstance(record, dict):
        raise ValueError("Invalid lifecycle")
    participants = record.get("participants")
    if (not isinstance(record.get("id"), str)
            or type(record.get("closed")) is not bool
            or type(record.get("trackedFromCreation")) is not bool
            or not isinstance(participants, list) or not participants
            or not all(identity(item) for item in participants)):
        raise ValueError("Invalid lifecycle fields")
    if record["trackedFromCreation"]:
        if (not identity(record.get("origin")) or record["origin"] not in participants
                or not isinstance(record.get("creationTip"), str) or not record["creationTip"]):
            raise ValueError("Invalid creation evidence")
    elif record.get("origin") is not None or record.get("creationTip") is not None:
        raise ValueError("Inconsistent incomplete history")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["register", "inspect", "close"])
    parser.add_argument("--repo", required=True)
    parser.add_argument("--branch", required=True)
    parser.add_argument("--chat-id")
    parser.add_argument("--source", choices=["codex", "chatgpt"], default="codex")
    parser.add_argument("--host-id", default="")
    parser.add_argument("--created", action="store_true",
                        help="Only immediately after creating a fresh branch in this chat")
    args = parser.parse_args()
    if args.action == "register" and not args.chat_id:
        parser.error("register requires a verified --chat-id")
    if args.created and args.action != "register":
        parser.error("--created only applies to register")
    if args.source == "chatgpt" and args.host_id:
        parser.error("ChatGPT identities do not use --host-id")
    git(args.repo, "check-ref-format", "refs/heads/" + args.branch)
    common = Path(git(args.repo, "rev-parse", "--path-format=absolute", "--git-common-dir"))
    directory = common / "codex-branch-chats"
    key = hashlib.sha256(args.branch.encode()).hexdigest()
    path = directory / (key + ".json")
    if args.action == "inspect" and not path.exists():
        print(json.dumps({"branch": args.branch, "record": None,
                          "single_chat_candidate": False, "reason": "missing history"}))
        return
    directory.mkdir(exist_ok=True)
    with (directory / (key + ".lock")).open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        data = json.loads(path.read_text()) if path.exists() else {
            "version": 1, "branch": args.branch, "lifecycles": []}
        if (not isinstance(data, dict) or data.get("version") != 1
                or data.get("branch") != args.branch or not isinstance(data.get("lifecycles"), list)):
            raise ValueError("Unrecognized participation record; preserve it and skip archival")
        records = data["lifecycles"]
        for prior in records:
            validate_record(prior)
        record = records[-1] if records else None
        if args.action == "register":
            # Confirm existence before recording either creation or management.
            tip = git(args.repo, "rev-parse", "--verify", "refs/heads/" + args.branch)
            identity = {"source": args.source, "hostId": args.host_id, "threadId": args.chat_id}
            if args.created:
                if record and not record["closed"]:
                    raise ValueError("An open lifecycle exists; do not overwrite its history")
                record = {"id": str(uuid.uuid4()), "creationTip": tip,
                          "origin": identity, "trackedFromCreation": True,
                          "participants": [], "closed": False}
                records.append(record)
            elif record is None or record["closed"]:
                # Existing branches and reused names without creation evidence remain ineligible.
                record = {"id": str(uuid.uuid4()), "creationTip": None,
                          "origin": None, "trackedFromCreation": False,
                          "participants": [], "closed": False}
                records.append(record)
            if identity not in record["participants"]:
                record["participants"].append(identity)
        elif args.action == "close":
            if record is None:
                raise ValueError("No lifecycle to close")
            record["closed"] = True
        if args.action != "inspect":
            temporary = None
            try:
                with tempfile.NamedTemporaryFile(mode="w", dir=directory, delete=False) as out:
                    temporary = out.name
                    json.dump(data, out, indent=2)
                    out.write("\n")
                    out.flush()
                    os.fsync(out.fileno())
                os.replace(temporary, path)
            finally:
                if temporary and os.path.exists(temporary):
                    os.unlink(temporary)
        candidate = bool(record and not record["closed"] and record["trackedFromCreation"]
                         and record["origin"] and record["participants"] == [record["origin"]])
        print(json.dumps({"branch": args.branch, "record": record,
                          "single_chat_candidate": candidate}))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError, subprocess.CalledProcessError) as error:
        raise SystemExit(f"Participation unavailable; skip archival: {error}")
