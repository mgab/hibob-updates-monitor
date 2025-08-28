
# HiBob Employee Monitor

Monitor HiBob employee data with automatic change detection and browser cookie authentication. Modern, modular, and easy to use from the command line.


## Features

- **Automatic Authentication**: Extracts cookies from your browser (Firefox, Chrome, Safari, Edge)
- **Change Tracking**: Detects added, removed, and modified employees with field-level details
- **Smart Caching**: Maintains history of last 200 runs with deduplication
- **Multiple Output Formats**: Table, JSON, and CSV
- **Modular Architecture**: Clean, functional Python with dataclass models


## Installation and execution

### Option 1: Install as a uv tool from github

Install directly from GitHub:

```bash
uv tool install git+https://github.com/mgab/hibob-updates-monitor
```

Now you can run the tool from anywhere:

```bash
hibob-monitor --help
```

### Option 2: Clone and install as a tool in editable mode

Clone the repository:

```bash
git clone git@github.com:mgab/hibob-updates-monitor.git
uv tool install -e ./hibob-updates-monitor
```

Now you can run the tool from anywhere:

```bash
hibob-monitor --help
```

### Option 3: Clone and run from the project

```bash
git clone git@github.com:mgab/hibob-updates-monitor.git
```

Now you can run the tool from the directory containing the project:

```bash
cd ./hibob-updates-monitor
uv run -m hibob-monitor --help
```

## Usage

Log into HiBob in your browser, then run (the prefix might change depending on the installation option):

```bash
# Basic usage (change tracking enabled by default)
hibob-monitor --domain app.hibob.com

# Use a different browser (chrome, safari, edge)
hibob-monitor --domain app.hibob.com --browser chrome

# Print the list of employees instead of the changes detected
hibob-monitor --domain app.hibob.com --stdout-output employee_list

# Export to JSON
hibob-monitor --domain app.hibob.com --format json --employee_list_path employees.json

# Disable change tracking
hibob-monitor --domain app.hibob.com --disable-change-tracking
```

## Command Line Options

```txt
--domain DOMAIN              HiBob domain (required)
--browser {firefox,chrome,safari,edge}  Browser for cookie extraction (default: firefox)
--format {table,json,csv}    Output format (default: table)
--employee_list_path FILE    Save employee list to file
--stdout-output {changes,employee_list,none}   Output type (default: changes)
--disable-change-tracking    Turn off change detection
--cache-file FILE            Custom cache location
--log-file FILE              Custom log location
--setup-help                 Show setup instructions
```


## Change Tracking

By default, the tool tracks changes between runs:

- **Cache**: Stores last 200 employee snapshots (`data/employees_cache.json`)
- **Logs**: Records all changes with timestamps (`data/employee_changes.log`)
- **Detection**: Identifies added, removed, and modified employees
- **Field Changes**: Shows exactly what changed in each employee record

Example change log entry:

```txt
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
- [browser_cookie3](https://github.com/borisbabic/browser_cookie3) (installed automatically)
- Active HiBob session in a supported browser

## License

MIT License - see LICENSE file for details.
