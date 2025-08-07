#!/usr/bin/env python3
"""
HiBob Employee Monitor - Modular Functional Programming Version
Main entry point using modular structure with change tracking
"""

import sys
from typing import Optional
from .cli import create_argument_parser, show_setup_help
from .auth import authenticate_with_browser
from .employees import get_active_employees
from .output import handle_output
from .domain_utils import build_base_url
from .cache import get_latest_cache, save_cache
from .change_detection import compare_employee_lists, log_changes
from .config import DEFAULT_CACHE_CONFIG


def run_hibob_monitor(
    domain: str,
    browser: str,
    format_type: str,
    output_path: Optional[str] = None,
    enable_change_tracking: bool = True,
    cache_file: str = "data/employees_cache.json",
    log_file: str = "data/employee_changes.log",
) -> None:
    """Main application logic with change tracking."""
    print("🔍 HiBob Employee Monitor (Modular Functional Version)")
    print(f"📍 Domain: {domain}")
    print(f"🌐 Browser: {browser.title()}")
    if enable_change_tracking:
        print(f"📝 Change tracking: enabled (cache: {cache_file}, log: {log_file})")
    else:
        print("📝 Change tracking: disabled")
    print()

    # Authenticate
    success, cookies = authenticate_with_browser(domain, browser)

    if not success:
        print("\n❌ Authentication failed.")
        print("💡 Make sure you're logged into HiBob in your browser.")
        print("💡 Try a different browser with --browser option.")
        print("💡 Use --setup-help for detailed instructions.")
        sys.exit(1)

    # Fetch employees
    print("\n🔍 Fetching active employees...")
    base_url = build_base_url(domain)
    employee_list = get_active_employees(base_url, cookies)

    if not employee_list:
        print("❌ No active employees found.")
        sys.exit(1)

    print(f"\n📊 Found {employee_list.count} active employees")

    # Handle change tracking
    if enable_change_tracking:
        print("\n🔄 Checking for changes...")
        previous_employee_list = get_latest_cache(cache_file)

        if previous_employee_list is not None:
            change_report = compare_employee_lists(
                employee_list, previous_employee_list
            )

            if change_report.has_changes:
                print(
                    f"📈 Changes detected: {len(change_report.added)} added, {len(change_report.removed)} removed, {len(change_report.modified)} modified"
                )
                log_changes(change_report, log_file)
            else:
                print("✅ No changes detected since last run")
        else:
            print("📥 First run - creating initial cache")

        # Save current data to cache
        save_cache(employee_list, cache_file, DEFAULT_CACHE_CONFIG)

    # Output results
    handle_output(employee_list, format_type, output_path)


def main() -> None:
    """Main function."""
    parser = create_argument_parser()
    args = parser.parse_args()

    if args.setup_help:
        show_setup_help()
        return

    if not args.domain:
        parser.error("--domain is required (use --setup-help for setup instructions)")

    run_hibob_monitor(
        domain=args.domain,
        browser=args.browser,
        format_type=args.format,
        output_path=args.output,
        enable_change_tracking=not args.disable_change_tracking,
        cache_file=args.cache_file,
        log_file=args.log_file,
    )


if __name__ == "__main__":
    main()
