"""
Command-line interface and help functions
"""

import argparse
from .cookies import SupportedBrowsers
from .output import OutputFormats


def show_setup_help() -> None:
    """Show setup instructions."""
    print("""
🚀 HiBob Employee Monitor Setup Guide (Modular Functional Version)

1. Install browser_cookie3:
   pip install browser_cookie3

2. Log into HiBob in your browser:
   • Firefox (default) - just make sure you're logged in
   • Chrome - use --browser chrome
   • Safari - use --browser safari (macOS only)
   • Edge - use --browser edge

3. Run the tool:
   python3 hibob_monitor --domain yourcompany.hibob.com

🔧 Browser-specific notes:
   • Firefox: Works best when Firefox is closed
   • Chrome: May need keychain access on macOS
   • Safari: May need keychain access on macOS

💡 If extraction fails, try a different browser with --browser option
""")


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        description="Download active employees from HiBob using automatic browser cookie extraction (Modular Functional Programming Version)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 hibob_monitor --domain mycompany.hibob.com
  python3 hibob_monitor --domain mycompany.hibob.com --browser chrome
  python3 hibob_monitor --domain mycompany.hibob.com --format json --output employees.json
  python3 hibob_monitor --domain mycompany.hibob.com --disable-change-tracking

Change Tracking (enabled by default):
  • Automatically detects added, removed, and modified employees
  • Keeps cache of last 20 runs with smart deduplication
  • Logs changes to plain text file with timestamps
  • Use --disable-change-tracking to turn off

Supported browsers: firefox (default), chrome, safari, edge
        """
    )
    
    parser.add_argument('--domain',
                       help='HiBob domain (e.g., mycompany.hibob.com)')
    parser.add_argument('--browser', 
                       choices=[browser.value for browser in SupportedBrowsers], 
                       default='firefox',
                       help='Browser to extract cookies from (default: firefox)')
    parser.add_argument('--format', choices=[fmt.value for fmt in OutputFormats], default='table',
                       help='Output format (default: table)')
    parser.add_argument('--output', '-o',
                       help='Output file path')
    parser.add_argument('--setup-help', action='store_true',
                       help='Show setup instructions')
    
    # Change tracking options
    parser.add_argument('--disable-change-tracking', action='store_true',
                       help='Disable change tracking (enabled by default)')
    parser.add_argument('--cache-file', default='data/employees_cache.json',
                       help='Cache file path (default: data/employees_cache.json)')
    parser.add_argument('--log-file', default='data/employee_changes.log',
                       help='Changes log file path (default: data/employee_changes.log)')
    
    return parser
