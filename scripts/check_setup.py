"""Check that this machine can run the workshop.

Tests one thing at a time and names the fix when something fails.

    python scripts/check_setup.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FAILED: list[str] = []


def ok(msg: str) -> None:
    print(f"  ok    {msg}")


def fail(msg: str, fix: str) -> None:
    print(f"  FAIL  {msg}")
    print(f"        fix: {fix}")
    FAILED.append(msg)


def check_python() -> None:
    print("Python")
    v = sys.version_info
    if (v.major, v.minor) >= (3, 11):
        ok(f"version {v.major}.{v.minor}.{v.micro}")
    else:
        fail(
            f"version {v.major}.{v.minor} is too old",
            "install Python 3.11 or newer, then rebuild .venv",
        )
    if (ROOT / ".venv") in Path(sys.executable).parents:
        ok("running inside the project .venv")
    else:
        print(f"  note  interpreter is {sys.executable}")
        print("        if imports fail, run: source .venv/bin/activate")


def check_packages() -> None:
    print("\nPackages")
    for name in ("openai", "dotenv", "numpy", "pydantic", "requests"):
        try:
            __import__(name)
            ok(name)
        except ImportError:
            fail(f"{name} is not installed", "python -m pip install -r requirements.txt")


def check_env() -> tuple[str, str] | None:
    print("\nConfiguration")
    try:
        from dotenv import load_dotenv
    except ImportError:
        fail("cannot read .env", "python -m pip install -r requirements.txt")
        return None

    env_file = ROOT / ".env"
    if not env_file.is_file():
        fail(".env does not exist", "cp .env.example .env, then add your key")
        return None
    ok(".env found")
    load_dotenv(env_file, override=True)

    base_url = (os.environ.get("AKAMAI_BASE_URL") or "").strip().rstrip("/")
    api_key = (os.environ.get("AKAMAI_API_KEY") or "").strip()

    if not base_url:
        fail("AKAMAI_BASE_URL is empty", "set it in .env")
    elif not base_url.endswith("/v1"):
        fail(
            f"AKAMAI_BASE_URL is {base_url!r} and does not end in /v1",
            "add the /v1 suffix, otherwise every request returns 404",
        )
    else:
        ok(f"AKAMAI_BASE_URL {base_url}")

    if not api_key or api_key == "paste_your_key_here":
        fail("AKAMAI_API_KEY is not set", "see docs/get-an-api-key.md")
    else:
        ok(f"AKAMAI_API_KEY loaded, {len(api_key)} characters, value hidden")

    if FAILED:
        return None
    return base_url, api_key


def check_endpoint(base_url: str, api_key: str) -> None:
    print("\nEndpoint")
    from openai import OpenAI

    client = OpenAI(base_url=base_url, api_key=api_key, timeout=30.0, max_retries=0)

    try:
        models = sorted(m.id for m in client.models.list().data)
    except Exception as exc:  # noqa: BLE001
        detail = str(exc)[:200]
        if "401" in detail:
            fix = "the key is wrong or has stray whitespace, see docs/get-an-api-key.md"
        elif "404" in detail:
            fix = "check AKAMAI_BASE_URL ends in /v1"
        else:
            fix = "see docs/troubleshooting.md"
        fail(f"cannot list models: {detail}", fix)
        return
    ok(f"{len(models)} model(s) served")
    for m in models:
        print(f"        {m}")

    expected = "qwen3-8-27b"
    if expected not in models:
        print(f"  note  {expected} is not in the list")
        print("        the notebooks default to it, pick another from the list above")
        return

    try:
        r = client.chat.completions.create(
            model=expected,
            messages=[{"role": "user", "content": "Reply with the single word: ready"}],
            max_tokens=10,
            temperature=0.0,
        )
    except Exception as exc:  # noqa: BLE001
        fail(f"completion failed: {str(exc)[:200]}", "see docs/troubleshooting.md")
        return
    answer = (r.choices[0].message.content or "").strip()
    ok(f"{expected} answered {answer!r}")


def main() -> int:
    print("Akamai Cloud Inference workshop, setup check\n")
    check_python()
    check_packages()
    config = check_env()
    if config:
        check_endpoint(*config)

    print()
    if FAILED:
        print(f"{len(FAILED)} check(s) failed. Fix the lines marked FAIL above.")
        print("More detail in docs/troubleshooting.md")
        return 1
    print("All checks passed. Open the notebooks with: jupyter notebook")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
