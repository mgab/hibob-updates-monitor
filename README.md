# HiBob Employee Monitor

A Python tool for monitoring HiBob employee data with automatic change detection and browser cookie authentication.

## Features

- **Automatic Authentication**: Extracts cookies from your browser (Firefox, Chrome, Safari, Edge)
- **Change Tracking**: Detects added, removed, and modified employees with detailed field-level changes
- **Smart Caching**: Maintains history of last 5 runs with intelligent deduplication
- **Multiple Output Formats**: Table, JSON, and CSV export options
- **Modular Architecture**: Clean, functional programming approach with dataclass models

## Quick Start

### Usage

```bash
# Basic usage (change tracking enabled by default)
uv run -m hibob_monitor --domain mycompany.hibob.com

# Different browser
uv run -m hibob_monitor --domain mycompany.hibob.com --browser chrome

# Export to JSON
uv run -m hibob_monitor --domain mycompany.hibob.com --format json --output employees.json

# Disable change tracking
uv run -m hibob_monitor --domain mycompany.hibob.com --disable-change-tracking

```

### Setup

1. Log into HiBob in your browser
2. Run the tool with your company's HiBob domain
3. The tool automatically extracts authentication cookies

### Development Setup

```bash
# Clone the repository
git clone <repository-url>
cd hibobMonitor

# Install dependencies
pip install browser_cookie3

# Run from source
python -m hibob_monitor --domain mycompany.hibob.com

# Build package (if using uv)
pip install uv
uv build
```

## Change Tracking

By default, the tool tracks changes between runs:

- **Cache**: Stores last 5 employee snapshots (`data/employees_cache.json`)
- **Logs**: Records all changes with timestamps (`data/employee_changes.log`)
- **Detection**: Identifies added, removed, and modified employees
- **Field Changes**: Shows exactly what changed in each employee record

Example change log entry:
```
============================================================
Changes detected at 2025-08-06 13:30:45
Compared with data from 2025-08-06 09:15:22
============================================================

📈 ADDED EMPLOYEES (1):
  + John Doe (ID: 12345, Email: john.doe@company.com)

📝 MODIFIED EMPLOYEES (1):
  ~ Jane Smith (ID: 67890, Email: jane.smith@company.com)
    department: Engineering → Product
    title: Developer → Senior Developer
```

## Command Line Options

```
--domain DOMAIN              HiBob domain (required)
--browser {firefox,chrome,safari,edge}  Browser for cookie extraction
--format {table,json,csv}    Output format
--output FILE                Save to file
--disable-change-tracking    Turn off change detection
--cache-file FILE            Custom cache location
--log-file FILE              Custom log location
--setup-help                 Show detailed setup instructions
```

## Architecture

The tool uses a modular functional programming approach:

- `hibob_monitor/models.py` - Dataclass models for type safety
- `hibob_monitor/auth.py` - Browser cookie authentication
- `hibob_monitor/employees.py` - Employee data fetching and filtering
- `hibob_monitor/cache.py` - Smart caching with deduplication
- `hibob_monitor/change_detection.py` - Change analysis and logging
- `hibob_monitor/output.py` - Multiple output format support
- `hibob_monitor/__main__.py` - Main entry point

## Browser Support

| Browser | Status | Notes |
|---------|--------|-------|
| Firefox | ✅ Recommended | Works best when browser is closed |
| Chrome | ✅ Good | May need keychain access on macOS |
| Safari | ✅ Good | May need keychain access on macOS |
| Edge | ✅ Good | Cross-platform support |

## Troubleshooting

**Authentication failed?**
- Make sure you're logged into HiBob in your browser
- Try a different browser with `--browser` option
- Close the browser and try again (especially for Firefox)

**No employees found?**
- Verify the domain name is correct
- Check if your account has permission to view employee data

**Cache issues?**
- Delete the cache file and run again for a fresh start
- Check file permissions in the `data/` directory

## Requirements

- Python 3.8+
- browser_cookie3 library
- Active HiBob session in supported browser

## License

MIT License - see LICENSE file for details.
