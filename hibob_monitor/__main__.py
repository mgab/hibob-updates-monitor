#!/usr/bin/env python3
"""
HiBob Employee Monitor - Modular Functional Programming Version
Main entry point using modular structure with change tracking
"""

import logging
from pathlib import Path
import sys
from typing import Optional, assert_never

from hibob_monitor.cookies import SupportedBrowser
from .cli import create_argument_parser, show_setup_help, OutputInfo
from .auth import authenticate_with_browser
from .employees import get_active_employees
from .output import append_to_file
from .output import format_change_report_as_text, OutputFormat, write_to_file
from .domain_utils import build_base_url
from .cache import get_latest_cache, save_cache
from .change_detection import compare_employee_lists
from .config import DEFAULT_CACHE_CONFIG
from .models import EmployeeList, ChangeReport


logger = logging.getLogger(__name__)


def setup_logging() -> None:
    """Setup logging to stderr."""
    logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stderr)


def run_hibob_monitor(
    domain: str,
    browser: SupportedBrowser,
    cache_file: Path,
    log_file: Path,
    list_format: OutputFormat = OutputFormat.TABLE,
    employee_list_path: Optional[Path] = None,
    output: OutputInfo = OutputInfo.CHANGES,
    enable_change_tracking: bool = True,
) -> None:
    """Main application logic with change tracking."""

    logger.info("🔍 HiBob Employee Monitor")
    logger.info(f"📍 Domain: {domain}")
    logger.info(f"🌐 Browser: {browser.value.title()}")
    if enable_change_tracking:
        logger.info(
            f"📝 Change tracking: enabled (cache: {cache_file}, log: {log_file})"
        )
    else:
        logger.info("📝 Change tracking: disabled")
    logger.info("")

    employee_list = fetch_new_employee_list(domain, browser)

    if not employee_list:
        logger.error("❌ No active employees found.")
        sys.exit(1)

    logger.info(f"\n📊 Found {employee_list.count} active employees")

    formatted_list = list_format.format(employee_list)
    if employee_list_path:
        logger.info(employee_list_path)
        success = write_to_file(formatted_list, employee_list_path)
        if success:
            logger.info(
                f"📄 Employee list saved as {list_format.value} to {employee_list_path}"
            )

    # Handle change tracking
    change_report_text = None
    if enable_change_tracking:
        logger.info("\n🔄 Checking for changes...")
        change_report = get_changes_since_latest_cache(employee_list, cache_file)

        if change_report is None:
            logger.info("📥 First run - creating initial cache")
        elif not change_report.has_changes:
            logger.info("✅ No changes detected since last run")
        else:
            logger.info(
                f"📈 Changes detected: {len(change_report.added)} added, {len(change_report.removed)} removed, {len(change_report.modified)} modified"
            )
            change_report_text = format_change_report_as_text(change_report)
            # Append to the log file
            success = append_to_file(change_report_text, log_file)

            if success:
                logger.info(
                    f"📝 {change_report.total_changes} changes logged to {log_file}"
                )
            else:
                logger.warning(f"⚠️  Warning: Could not write to log file {log_file}")

        # Save current data to cache
        save_cache(employee_list, cache_file, DEFAULT_CACHE_CONFIG)

    match output:
        case OutputInfo.CHANGES:
            if change_report_text is not None:
                sys.stdout.write(change_report_text)
        case OutputInfo.EMPLOYEE_LIST:
            sys.stderr.write(formatted_list)
        case OutputInfo.NONE:
            pass
        case _:
            assert_never(output)


def fetch_new_employee_list(
    domain: str, browser: SupportedBrowser
) -> EmployeeList | None:
    # Authenticate
    success, cookies = authenticate_with_browser(domain, browser)

    if not success:
        logger.error("\n❌ Authentication failed.")
        logger.info("💡 Make sure you're logged into HiBob in your browser.")
        logger.info("💡 Try a different browser with --browser option.")
        logger.info("💡 Use --setup-help for detailed instructions.")
        sys.exit(1)

    # Fetch employees
    logger.info("\n🔍 Fetching active employees...")
    base_url = build_base_url(domain)
    return get_active_employees(base_url, cookies)


def get_changes_since_latest_cache(
    employee_list: EmployeeList, cache_file: Path
) -> Optional[ChangeReport]:
    """Get changes since the latest cache."""
    previous_employee_list = get_latest_cache(cache_file)
    if previous_employee_list is not None:
        return compare_employee_lists(employee_list, previous_employee_list)
    return None


def get_change_report_since_latest_run(
    employee_list: EmployeeList, cache_file: Path
) -> ChangeReport | None:
    """Get the change report since the latest run."""
    logger.info("\n🔄 Checking for changes...")
    previous_employee_list = get_latest_cache(cache_file)

    if previous_employee_list is not None:
        change_report = compare_employee_lists(employee_list, previous_employee_list)

        if change_report.has_changes:
            logger.info(
                f"📈 Changes detected: {len(change_report.added)} added, {len(change_report.removed)} removed, {len(change_report.modified)} modified"
            )
        else:
            logger.info("✅ No changes detected since last run")
        return change_report
    else:
        return None


def main() -> None:
    """Main function."""
    setup_logging()

    parser = create_argument_parser()
    args = parser.parse_args()

    if args.setup_help:
        show_setup_help()
        return

    if not args.domain:
        parser.error("--domain is required (use --setup-help for setup instructions)")

    if args.output == OutputInfo.CHANGES and args.disable_change_tracking:
        parser.error("Change tracking must be enabled to output changes.")

    run_hibob_monitor(
        domain=args.domain,
        browser=args.browser,
        list_format=args.format,
        employee_list_path=args.employee_list_path,
        output=args.output,
        enable_change_tracking=not args.disable_change_tracking,
        cache_file=args.cache_file,
        log_file=args.log_file,
    )


if __name__ == "__main__":
    main()
