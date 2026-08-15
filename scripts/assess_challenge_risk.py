"""
CLI for the pre-award challenge risk screen (src/risk/challenge_risk.py).

Fill in what you actually know about this procurement BEFORE the standstill letter goes out — leave
everything else unset. An unset field contributes nothing to the score; a guessed field is worse than an
unset one, because it produces a false sense of having screened for something you didn't actually check.

Usage:
    python scripts/assess_challenge_risk.py \
        --documentation-quality weak \
        --score-margin narrow \
        --feedback-quality-received minimal \
        --json out.json

    python scripts/assess_challenge_risk.py --list-fields   # see every available flag and its choices
"""

import argparse
import json
import sys
from pathlib import Path
from typing import get_args

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.risk.challenge_risk import assess_challenge_risk
from src.schemas.agent_state import BidderProfile, CAProfile


def _add_model_flags(parser: argparse.ArgumentParser, model, prefix: str) -> None:
    """Adds one --flag per field on a Pydantic model, using the field's own Literal/bool type as choices."""
    for name, field in model.model_fields.items():
        flag = f"--{prefix}-{name.replace('_', '-')}"
        annotation = field.annotation
        # Optional[X] -> X
        args = get_args(annotation)
        inner = args[0] if args and type(None) in args else annotation
        if inner is bool:
            parser.add_argument(flag, action="store_true", default=None, dest=f"{prefix}__{name}")
        else:
            choices = get_args(inner) or None
            parser.add_argument(flag, choices=choices, default=None, dest=f"{prefix}__{name}")


def _build_model(model_cls, args: argparse.Namespace, prefix: str):
    kwargs = {}
    for name in model_cls.model_fields:
        value = getattr(args, f"{prefix}__{name}", None)
        if value is not None:
            kwargs[name] = value
    return model_cls(**kwargs) if kwargs else model_cls()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list-fields", action="store_true", help="print every available flag and exit")
    ap.add_argument("--json", metavar="PATH", help="write the full assessment as JSON to this path")
    _add_model_flags(ap, CAProfile, "ca")
    _add_model_flags(ap, BidderProfile, "bidder")
    args = ap.parse_args()

    if args.list_fields:
        print("CA profile fields (things the authority itself knows/controls):")
        for name, field in CAProfile.model_fields.items():
            args_t = get_args(field.annotation)
            inner = args_t[0] if args_t and type(None) in args_t else field.annotation
            choices = get_args(inner) or ("flag, no value" if inner is bool else "?")
            print(f"  --ca-{name.replace('_', '-'):35s} {choices}")
        print("\nBidder profile fields (some known, some estimated — see module docstring):")
        for name, field in BidderProfile.model_fields.items():
            args_t = get_args(field.annotation)
            inner = args_t[0] if args_t and type(None) in args_t else field.annotation
            choices = get_args(inner) or ("flag, no value" if inner is bool else "?")
            print(f"  --bidder-{name.replace('_', '-'):35s} {choices}")
        sys.exit(0)

    ca_profile = _build_model(CAProfile, args, "ca")
    bidder_profile = _build_model(BidderProfile, args, "bidder")

    result = assess_challenge_risk(ca_profile, bidder_profile)

    print(f"\n{'=' * 70}")
    print("  PRE-AWARD CHALLENGE RISK SCREEN")
    print(f"{'=' * 70}")
    print(f"Overall band: {result.overall_risk_band.upper()}  (score {result.risk_score})")
    print(f"\n{result.summary}\n")

    if result.flags:
        print(f"{len(result.flags)} flag(s):\n")
        for f in sorted(result.flags, key=lambda x: -{"high": 3, "medium": 2, "low": 1}[x.severity]):
            print(f"[{f.severity.upper():6s}][{f.confidence:9s}] {f.category}")
            print(f"  Field:      {f.field}")
            print(f"  Why:        {f.rationale}")
            print(f"  Mitigate:   {f.mitigation}\n")
    else:
        print("No fields were populated — run with --list-fields to see what this screen can check, "
              "or fill in what you actually know about this procurement.")

    if args.json:
        Path(args.json).write_text(result.model_dump_json(indent=2), encoding="utf-8")
        print(f"Full assessment written to {args.json}")
