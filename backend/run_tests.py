#!/usr/bin/env python
"""
STORICA test runner with progress output and fast defaults.

Uses ``config.settings_test`` (MD5 password hasher, quiet logs) unless
``DJANGO_SETTINGS_MODULE`` is already set in the environment.

Examples
--------
  python run_tests.py
  python run_tests.py apps.inventory
  python run_tests.py apps.sales --parallel 4
  python run_tests.py --no-keepdb          # recreate test DB
  python run_tests.py -v 1 --failfast
  python run_tests.py -k low_stock
  python manage.py test apps.inventory --settings=config.settings_test --keepdb
"""
from __future__ import annotations

import argparse
import os
import sys
import time


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run STORICA Django tests (fast defaults)."
    )
    parser.add_argument(
        "labels",
        nargs="*",
        default=[
            "apps.inventory",
            "apps.sales",
            "apps.purchases",
            "apps.users",
            "apps.accounting",
        ],
        help="Test labels (default: main apps)",
    )
    parser.add_argument(
        "-v",
        "--verbosity",
        type=int,
        default=1,
        help="Verbosity (default: 1; use 2 for per-test lines)",
    )
    parser.add_argument("--failfast", action="store_true")
    parser.add_argument(
        "-k",
        "--pattern",
        action="append",
        default=None,
        help="Filter tests by name substring (may be repeated)",
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Set STORICA_TEST_FAST=1 for suite-level shortcuts",
    )
    parser.add_argument(
        "--keepdb",
        dest="keepdb",
        action="store_true",
        default=True,
        help="Reuse test database (default: on)",
    )
    parser.add_argument(
        "--no-keepdb",
        dest="keepdb",
        action="store_false",
        help="Drop and recreate the test database",
    )
    parser.add_argument(
        "--parallel",
        nargs="?",
        const="auto",
        default=0,
        help="Parallel processes: omit value for 'auto', or pass N",
    )
    parser.add_argument(
        "--prod-settings",
        action="store_true",
        help="Use config.settings instead of config.settings_test",
    )
    args = parser.parse_args()

    if args.prod_settings:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    else:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings_test")

    if args.fast:
        os.environ["STORICA_TEST_FAST"] = "1"

    import django
    from django.conf import settings
    from django.test.utils import get_runner

    django.setup()

    parallel = args.parallel
    if parallel in (None, 0, "0"):
        parallel = 0
    elif parallel != "auto":
        try:
            parallel = int(parallel)
        except (TypeError, ValueError):
            print(f"Invalid --parallel value: {parallel!r}", file=sys.stderr)
            return 2

    runner_kwargs: dict = {
        "verbosity": args.verbosity,
        "interactive": False,
        "failfast": args.failfast,
        "keepdb": args.keepdb,
    }
    if parallel:
        runner_kwargs["parallel"] = parallel
    if args.pattern:
        runner_kwargs["test_name_patterns"] = args.pattern

    TestRunner = get_runner(settings)
    runner = TestRunner(**runner_kwargs)

    labels = list(args.labels)

    print("=" * 60)
    print("STORICA test run")
    print(f"  settings  : {os.environ.get('DJANGO_SETTINGS_MODULE')}")
    print(f"  labels    : {', '.join(labels)}")
    print(f"  verbosity : {args.verbosity}")
    print(f"  failfast  : {args.failfast}")
    print(f"  keepdb    : {args.keepdb}")
    print(f"  parallel  : {parallel or 'off'}")
    if args.pattern:
        print(f"  pattern   : {args.pattern}")
    print("=" * 60)

    started = time.perf_counter()
    failures = runner.run_tests(labels)
    elapsed = time.perf_counter() - started

    print("=" * 60)
    print(f"Finished in {elapsed:.1f}s — failures={failures}")
    print("=" * 60)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
