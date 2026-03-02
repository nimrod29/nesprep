"""CSV template generator for shift planning.

Generates fresh CSV templates with correct dates for any month.
Weeks run Sunday-Saturday (Israeli work week).
"""

import csv
import io
from calendar import monthrange
from datetime import date, timedelta

HEBREW_DAYS = ["ראשון", "שני", "שלישי", "רביעי", "חמישי", "שישי", "שבת"]

# Week block structure - each week has this many rows
WEEK_BLOCK_ROWS = 27

# Row offsets within a week block (0-indexed)
WEEK_EVENTS_ROW = 0
WEEK_TASKS_ROW = 1
BENEFITS_ROW = 2
DAY_HEADERS_ROW = 3
DATE_ROW = 4
EMPTY_ROW_1 = 5
MORNING_SHIFT_START = 6  # 09:00-18:00, rows 6-10 (5 slots)
AFTERNOON_SHIFT_START = 11  # 10:00-19:00, 11:00-20:00, 12:00-21:00
EMPTY_ROW_2 = 14
EVENING_SHIFT_START = 15  # 13:00-22:00, rows 15-20 (6 slots)
REFRESH_ROW = 21
NOTES_ROW_1 = 22
NOTES_ROW_2 = 23
# Rows 24-26 are empty/padding


def get_weeks_in_month(year: int, month: int) -> list[tuple[date, date]]:
    """Get all weeks (Sunday-Saturday) that overlap with the given month.
    
    Returns list of (week_start_sunday, week_end_saturday) tuples.
    A week is included if any day falls within the target month.
    """
    _, days_in_month = monthrange(year, month)
    first_day = date(year, month, 1)
    last_day = date(year, month, days_in_month)
    
    # Find the Sunday on or before the first day of the month
    days_since_sunday = first_day.weekday()
    # Python weekday: Monday=0, Sunday=6
    # We need: Sunday=0, Saturday=6
    # Convert: (weekday + 1) % 7 gives us Sunday=0
    days_since_sunday = (first_day.weekday() + 1) % 7
    first_sunday = first_day - timedelta(days=days_since_sunday)
    
    weeks = []
    current_sunday = first_sunday
    
    while True:
        current_saturday = current_sunday + timedelta(days=6)
        
        # Check if this week overlaps with the month
        week_overlaps = (
            (current_sunday.month == month and current_sunday.year == year) or
            (current_saturday.month == month and current_saturday.year == year) or
            (current_sunday <= first_day <= current_saturday) or
            (current_sunday <= last_day <= current_saturday)
        )
        
        if week_overlaps:
            weeks.append((current_sunday, current_saturday))
        
        # Move to next week
        current_sunday = current_sunday + timedelta(days=7)
        
        # Stop if we've passed the month entirely
        if current_sunday > last_day and current_sunday.month != month:
            break
    
    return weeks


def generate_week_block(week_start: date) -> list[list[str]]:
    """Generate CSV rows for one week with dates filled in.
    
    Args:
        week_start: The Sunday that starts this week.
        
    Returns:
        List of rows, each row is a list of cell values.
    """
    rows: list[list[str]] = []
    
    # Calculate dates for each day (Sunday to Saturday)
    dates = [week_start + timedelta(days=i) for i in range(7)]
    date_strings = [f"{d.day}.{d.month}" for d in dates]
    
    # Row 0: Weekly events
    rows.append(["אירועי השבוע"] + [""] * 7)
    
    # Row 1: Weekly tasks
    rows.append(["משימות שבועיות"] + [""] * 7)
    
    # Row 2: Benefits
    rows.append(["הטבות"] + [""] * 7)
    
    # Row 3: Day headers
    rows.append([""] + HEBREW_DAYS)
    
    # Row 4: Date row with actual dates
    rows.append(["תאריך"] + date_strings)
    
    # Row 5: Empty
    rows.append([""] * 8)
    
    # Rows 6-10: Morning shifts (09:00-18:00) - 5 slots
    rows.append(["09:00-18:00"] + [""] * 7)
    for _ in range(4):
        rows.append([""] * 8)
    
    # Rows 11-13: Afternoon shifts
    rows.append(["10:00-19:00"] + [""] * 7)
    rows.append(["11:00-20:00"] + [""] * 7)
    rows.append(["12:00-21:00"] + [""] * 7)
    
    # Row 14: Empty
    rows.append([""] * 8)
    
    # Rows 15-20: Evening shifts (13:00-22:00) - 6 slots
    rows.append(["13:00-22:00"] + [""] * 7)
    for _ in range(5):
        rows.append([""] * 8)
    
    # Row 21: Refresh/training
    rows.append(["רענון"] + [""] * 7)
    
    # Rows 22-23: Notes
    rows.append(["הערות"] + [""] * 7)
    rows.append(["הערות"] + [""] * 7)
    
    # Rows 24-26: Padding/empty
    for _ in range(3):
        rows.append([""] * 8)
    
    return rows


def generate_month_template(year: int, month: int) -> str:
    """Generate complete CSV template for a month.
    
    Args:
        year: The year (e.g., 2025)
        month: The month (1-12)
        
    Returns:
        CSV content as a string.
    """
    hebrew_months = {
        1: "ינואר", 2: "פברואר", 3: "מרץ", 4: "אפריל",
        5: "מאי", 6: "יוני", 7: "יולי", 8: "אוגוסט",
        9: "ספטמבר", 10: "אוקטובר", 11: "נובמבר", 12: "דצמבר"
    }
    
    weeks = get_weeks_in_month(year, month)
    
    if not weeks:
        raise ValueError(f"No weeks found for {year}-{month:02d}")
    
    all_rows: list[list[str]] = []
    
    # Header row with month title
    month_name = hebrew_months.get(month, str(month))
    all_rows.append([f"סידור עובדים - {month_name} {year}"] + [""] * 7)
    
    # Empty rows before first week
    for _ in range(5):
        all_rows.append([""] * 8)
    
    # Generate each week block
    for week_start, _ in weeks:
        week_rows = generate_week_block(week_start)
        all_rows.extend(week_rows)
    
    # Convert to CSV string
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerows(all_rows)
    
    return output.getvalue()


def save_month_template(year: int, month: int, output_path: str) -> str:
    """Generate and save a month template to a file.
    
    Args:
        year: The year
        month: The month (1-12)
        output_path: Path to save the CSV file
        
    Returns:
        The output path.
    """
    csv_content = generate_month_template(year, month)
    
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        f.write(csv_content)
    
    return output_path
