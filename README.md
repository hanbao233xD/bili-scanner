# Bilibili Account Scanner

This tool scans Bilibili user accounts to find those that meet specific criteria:
- Username consists of pure English letters and numbers (e.g., test123)
- Account level is 0

## Features

- Automated browser-based scanning using Selenium
- Intelligent retry mechanism for handling network issues
- Progress tracking and periodic saving of results
- Detection and skipping of verification/captcha pages
- Configurable delays to avoid being blocked

## Requirements

- Python 3.7+
- Chrome browser
- Required Python packages:
  - selenium
  - webdriver-manager

## Installation

1. Install the required packages:
```bash
pip install selenium webdriver-manager
```

2. No additional setup is required. The script will automatically download and manage ChromeDriver.

## Usage

Run the scanner:
```bash
python bili_browser_scanner.py
```

The script will:
1. Start scanning from UID 1
2. Save valid UIDs to `valid_uids.txt` every 10 matches
3. Display progress information in the console
4. Handle errors and retries automatically

## Output

Valid UIDs are saved to `valid_uids.txt` in the same directory. Each line contains one UID that meets the criteria.

## Notes

- The scanning process can be stopped at any time with Ctrl+C
- When stopped, any remaining valid UIDs in memory will be saved
- The script includes random delays to avoid overwhelming the server
- If verification pages (captchas) are detected, those UIDs will be skipped

## Customization

You can modify the scanning criteria by editing the `is_valid_username()` and condition checks in `scan_accounts()` function.