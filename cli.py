#!/usr/bin/env python3
"""
CLI for 12-Lead ECG Interpretation Helper.

Provides commands for ECG interval analysis, axis calculation,
STEMI detection, and bundle branch block evaluation.
"""
import argparse
import json
import sys

from ecg_interpretation import (
    ALL_LEADS,
    LEAD_INFO,
    STEMI_TERRITORIES,
    BBB_CRITERIA,
    NORMAL_INTERVALS,
    calculate_axis_from_leads,
    classify_axis,
    check_intervals,
    check_st_elevation,
    check_bundle_branch_block,
    calculate_qtc_bazett,
    calculate_qtc_fridericia,
    hr_from_rr,
    rr_from_hr,
    interpret_ecg,
    get_lead_info,
    get_all_lead_info,
)


def cmd_intervals(args):
    """Check ECG intervals against normal ranges."""
    rr = args.rr
    if rr is None and args.hr is not None and args.hr > 0:
        rr = rr_from_hr(args.hr)

    result = check_intervals(
        pr_ms=args.pr,
        qrs_ms=args.qrs,
        qt_ms=args.qt,
        rr_seconds=rr,
        sex=args.sex,
    )

    print("=" * 60)
    print("  ECG INTERVAL ANALYSIS")
    print("=" * 60)
    for name, info in result["intervals"].items():
        status = info.get("status", "N/A")
        val = info.get("value_ms", "N/A")
        print(f"  {name.upper():6s}: {val} ms  [{status}]")

    if result["abnormalities"]:
        print("\n  ABNORMALITIES:")
        for abn in result["abnormalities"]:
            print(f"    - {abn['finding']}: {abn['value']}")
            print(f"      {abn['significance']}")
    else:
        print("\n  All intervals within normal limits.")

    if args.json:
        print("\n" + json.dumps(result, indent=2))
    return 0


def cmd_axis(args):
    """Calculate frontal plane QRS axis."""
    axis = calculate_axis_from_leads(args.lead_i, args.lead_avf)
    classification = classify_axis(axis)

    print("=" * 60)
    print("  FRONTAL PLANE QRS AXIS")
    print("=" * 60)
    print(f"  Lead I net amplitude:   {args.lead_i} mm")
    print(f"  Lead aVF net amplitude: {args.lead_avf} mm")
    print(f"  Calculated axis:        {classification['axis_degrees']} degrees")
    print(f"  Classification:         {classification['classification']}")
    print(f"  Clinical significance:  {classification['clinical_significance']}")

    if args.json:
        print("\n" + json.dumps(classification, indent=2))
    return 0


def cmd_stemi(args):
    """Check ST elevation for STEMI criteria."""
    elevations = {}
    if args.st_elevations:
        for item in args.st_elevations:
            parts = item.split(":")
            if len(parts) == 2:
                elevations[parts[0].strip()] = float(parts[1].strip())

    result = check_st_elevation(elevations)

    print("=" * 60)
    print("  ST ELEVATION / STEMI ANALYSIS")
    print("=" * 60)
    print(f"  STEMI criteria met: {'YES' if result['stemi_detected'] else 'NO'}")
    print(f"  Elevated leads: {result['num_elevated_leads']}")

    if result["elevated_leads"]:
        print("\n  ELEVATED LEADS:")
        for el in result["elevated_leads"]:
            print(f"    {el['lead']}: {el['elevation_mm']} mm (threshold: {el['threshold_mm']} mm)")

    if result["territories"]:
        print("\n  TERRITORIES INVOLVED:")
        for t in result["territories"]:
            print(f"    - {t['description']}")
            print(f"      Artery: {t['artery']}")
            print(f"      Leads: {', '.join(t['elevated_leads'])}")

    print(f"\n  {result['clinical_action']}")

    if args.json:
        print("\n" + json.dumps(result, indent=2))
    return 0


def cmd_bbb(args):
    """Evaluate for bundle branch block."""
    result = check_bundle_branch_block(
        qrs_ms=args.qrs,
        lead_v1_pattern=args.v1_pattern,
        lead_i_pattern=args.i_pattern,
        lead_v5_v6_pattern=args.v5v6_pattern,
        has_q_in_v5_v6=args.q_v5v6,
        has_q_in_i=args.q_i,
    )

    print("=" * 60)
    print("  BUNDLE BRANCH BLOCK ANALYSIS")
    print("=" * 60)
    print(f"  QRS duration: {result['qrs_ms']} ms")
    print(f"  QRS widened:  {'Yes' if result['qrs_widened'] else 'No'}")
    print(f"  Diagnosis:    {result['diagnosis']}")

    if result["criteria_details"]:
        print("\n  CRITERIA MET:")
        for c in result["criteria_details"]:
            print(f"    + {c}")

    if "clinical_significance" in result:
        print("\n  CLINICAL SIGNIFICANCE:")
        for s in result["clinical_significance"]:
            print(f"    - {s}")

    if args.json:
        print("\n" + json.dumps(result, indent=2))
    return 0


def cmd_qtc(args):
    """Calculate QTc using specified formula."""
    if args.rr is None and args.hr is not None and args.hr > 0:
        args.rr = rr_from_hr(args.hr)

    if args.rr is None:
        print("Error: must provide --rr or --hr", file=sys.stderr)
        return 1

    results = {}
    results["Bazett"] = round(calculate_qtc_bazett(args.qt, args.rr), 1)
    results["Fridericia"] = round(calculate_qtc_fridericia(args.qt, args.rr), 1)

    print("=" * 60)
    print("  QTc CALCULATION")
    print("=" * 60)
    print(f"  QT interval:  {args.qt} ms")
    print(f"  RR interval:  {args.rr} s (HR: {hr_from_rr(args.rr):.0f} bpm)")
    for formula, val in results.items():
        print(f"  QTc ({formula}): {val} ms")

    if args.json:
        print("\n" + json.dumps(results, indent=2))
    return 0


def cmd_leads(args):
    """Show lead placement information."""
    info = get_all_lead_info()
    print("=" * 70)
    print("  12-LEAD ECG PLACEMENT AND ANATOMICAL INFORMATION")
    print("=" * 70)
    for lead, data in info.items():
        print(f"\n  Lead {lead}:")
        if "placement" in data:
            print(f"    Placement: {data['placement']}")
        else:
            print(f"    Positive: {data['positive_electrode']}")
            print(f"    Negative: {data['negative_electrode']}")
        print(f"    Axis: {data['axis_degrees']} degrees")
        print(f"    Views: {data['views']}")
        print(f"    Territory: {data['coronary_territory']}")
    return 0


def cmd_interpret(args):
    """Run comprehensive ECG interpretation."""
    rr = args.rr
    if rr is None and args.hr is not None and args.hr > 0:
        rr = rr_from_hr(args.hr)

    st_elev = {}
    if args.st_elevations:
        for item in args.st_elevations:
            parts = item.split(":")
            if len(parts) == 2:
                st_elev[parts[0].strip()] = float(parts[1].strip())

    result = interpret_ecg(
        lead_i_amplitude=args.lead_i,
        lead_avf_amplitude=args.lead_avf,
        pr_ms=args.pr,
        qrs_ms=args.qrs,
        qt_ms=args.qt,
        rr_seconds=rr,
        sex=args.sex,
        st_elevations=st_elev if st_elev else None,
        lead_v1_pattern=args.v1_pattern,
        lead_i_pattern=args.i_pattern,
        lead_v5_v6_pattern=args.v5v6_pattern,
        has_q_in_v5_v6=args.q_v5v6,
        has_q_in_i=args.q_i,
    )

    print("=" * 60)
    print("  COMPREHENSIVE ECG INTERPRETATION")
    print("=" * 60)

    if result["analysis"].get("heart_rate"):
        print(f"  Heart Rate: {result['analysis']['heart_rate']} bpm")

    if result["analysis"].get("axis"):
        ax = result["analysis"]["axis"]
        print(f"  QRS Axis: {ax['axis_degrees']} deg ({ax['classification']})")

    if result["findings"]:
        print("\n  FINDINGS:")
        for f in result["findings"]:
            print(f"    - {f}")

    if result["warnings"]:
        print("\n  WARNINGS:")
        for w in result["warnings"]:
            print(f"    !! {w}")

    print(f"\n  SUMMARY: {result['summary']}")

    if args.json:
        print("\n" + json.dumps(result, indent=2))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="ecg-12lead",
        description="12-Lead ECG Interpretation Helper - Real clinical calculations",
    )
    parser.add_argument("--json", action="store_true", help="Also output JSON")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Intervals
    p_int = subparsers.add_parser("intervals", help="Check ECG intervals")
    p_int.add_argument("--pr", type=float, help="PR interval in ms")
    p_int.add_argument("--qrs", type=float, help="QRS duration in ms")
    p_int.add_argument("--qt", type=float, help="QT interval in ms")
    p_int.add_argument("--rr", type=float, help="RR interval in seconds")
    p_int.add_argument("--hr", type=float, help="Heart rate in bpm (used if --rr not given)")
    p_int.add_argument("--sex", choices=["male", "female"], default="male", help="Patient sex")

    # Axis
    p_ax = subparsers.add_parser("axis", help="Calculate frontal plane axis")
    p_ax.add_argument("--lead-i", type=float, required=True, help="Net QRS amplitude in lead I (mm)")
    p_ax.add_argument("--lead-avf", type=float, required=True, help="Net QRS amplitude in lead aVF (mm)")

    # STEMI
    p_st = subparsers.add_parser("stemi", help="Check ST elevation for STEMI")
    p_st.add_argument("--st-elevations", nargs="+", metavar="LEAD:MM",
                      help="ST elevations as LEAD:MM pairs, e.g. II:3 III:2.5 aVF:2")

    # BBB
    p_bbb = subparsers.add_parser("bbb", help="Evaluate bundle branch block")
    p_bbb.add_argument("--qrs", type=float, required=True, help="QRS duration in ms")
    p_bbb.add_argument("--v1-pattern", choices=["rsr", "rsR", "broadR", "qS", "other"], default="other")
    p_bbb.add_argument("--i-pattern", choices=["wideS", "broadNotchedR", "other"], default="other")
    p_bbb.add_argument("--v5v6-pattern", choices=["wideS", "broadNotchedR", "rsr", "other"], default="other")
    p_bbb.add_argument("--q-v5v6", action="store_true", help="Q waves present in V5/V6")
    p_bbb.add_argument("--q-i", action="store_true", help="Q waves present in I")

    # QTc
    p_qtc = subparsers.add_parser("qtc", help="Calculate QTc")
    p_qtc.add_argument("--qt", type=float, required=True, help="QT interval in ms")
    p_qtc.add_argument("--rr", type=float, help="RR interval in seconds")
    p_qtc.add_argument("--hr", type=float, help="Heart rate in bpm")

    # Leads
    subparsers.add_parser("leads", help="Show 12-lead placement info")

    # Comprehensive interpretation
    p_interp = subparsers.add_parser("interpret", help="Comprehensive ECG interpretation")
    p_interp.add_argument("--lead-i", type=float, help="Net QRS amplitude in lead I (mm)")
    p_interp.add_argument("--lead-avf", type=float, help="Net QRS amplitude in lead aVF (mm)")
    p_interp.add_argument("--pr", type=float, help="PR interval in ms")
    p_interp.add_argument("--qrs", type=float, help="QRS duration in ms")
    p_interp.add_argument("--qt", type=float, help="QT interval in ms")
    p_interp.add_argument("--rr", type=float, help="RR interval in seconds")
    p_interp.add_argument("--hr", type=float, help="Heart rate in bpm")
    p_interp.add_argument("--sex", choices=["male", "female"], default="male")
    p_interp.add_argument("--st-elevations", nargs="+", metavar="LEAD:MM")
    p_interp.add_argument("--v1-pattern", choices=["rsr", "rsR", "broadR", "qS", "other"], default="other")
    p_interp.add_argument("--i-pattern", choices=["wideS", "broadNotchedR", "other"], default="other")
    p_interp.add_argument("--v5v6-pattern", choices=["wideS", "broadNotchedR", "rsr", "other"], default="other")
    p_interp.add_argument("--q-v5v6", action="store_true")
    p_interp.add_argument("--q-i", action="store_true")

    args = parser.parse_args(argv)

    commands = {
        "intervals": cmd_intervals,
        "axis": cmd_axis,
        "stemi": cmd_stemi,
        "bbb": cmd_bbb,
        "qtc": cmd_qtc,
        "leads": cmd_leads,
        "interpret": cmd_interpret,
    }

    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
