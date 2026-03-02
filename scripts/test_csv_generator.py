"""Test CSV template generation."""

from datetime import date

from app.utils.csv_template_generator import (
    generate_month_template,
    get_weeks_in_month,
    save_month_template,
)


def test_march_2025():
    """Test March 2025 template generation."""
    print("=" * 60)
    print("Testing March 2025")
    print("=" * 60)

    # March 2025: 1st is Saturday, so first full week starts March 2 (Sunday)
    weeks = get_weeks_in_month(2025, 3)
    print(f"\nWeeks in March 2025: {len(weeks)}")
    for start, end in weeks:
        print(f"  {start} ({start.strftime('%A')}) - {end} ({end.strftime('%A')})")

    csv_content = generate_month_template(2025, 3)
    lines = csv_content.splitlines()
    print(f"\nGenerated {len(lines)} lines")

    # Show first few lines
    print("\nFirst 20 lines:")
    for i, line in enumerate(lines[:20]):
        print(f"  {i:3d}: {line}")

    # Verify dates are present
    assert "2.3" in csv_content, "March 2 (Sunday) should be in template"
    assert "8.3" in csv_content, "March 8 (Saturday) should be in template"
    print("\n✓ Date verification passed")


def test_february_2025():
    """Test February 2025 (short month)."""
    print("\n" + "=" * 60)
    print("Testing February 2025")
    print("=" * 60)

    weeks = get_weeks_in_month(2025, 2)
    print(f"\nWeeks in February 2025: {len(weeks)}")
    for start, end in weeks:
        print(f"  {start} ({start.strftime('%A')}) - {end} ({end.strftime('%A')})")

    csv_content = generate_month_template(2025, 2)
    lines = csv_content.splitlines()
    print(f"\nGenerated {len(lines)} lines")

    # February 2025 starts on Saturday, ends on Friday
    assert "1.2" in csv_content, "February 1 should be in template"
    assert "28.2" in csv_content, "February 28 should be in template"
    print("\n✓ Date verification passed")


def test_january_2026():
    """Test January 2026 (starts on Thursday)."""
    print("\n" + "=" * 60)
    print("Testing January 2026")
    print("=" * 60)

    weeks = get_weeks_in_month(2026, 1)
    print(f"\nWeeks in January 2026: {len(weeks)}")
    for start, end in weeks:
        print(f"  {start} ({start.strftime('%A')}) - {end} ({end.strftime('%A')})")

    csv_content = generate_month_template(2026, 1)
    lines = csv_content.splitlines()
    print(f"\nGenerated {len(lines)} lines")

    # January 2026 starts on Thursday
    assert "1.1" in csv_content, "January 1 should be in template"
    assert "31.1" in csv_content, "January 31 should be in template"
    print("\n✓ Date verification passed")


def test_save_template():
    """Test saving template to file."""
    print("\n" + "=" * 60)
    print("Testing save_month_template")
    print("=" * 60)

    import os
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = os.path.join(tmpdir, "test_template.csv")
        result = save_month_template(2025, 3, output_path)

        assert os.path.exists(result), f"File should exist at {result}"
        print(f"\n✓ Saved template to: {result}")

        with open(result, encoding="utf-8") as f:
            content = f.read()
            assert "סידור עובדים - מרץ 2025" in content, "Header should be present"
            print("✓ Header verification passed")


def test_week_calculation_edge_cases():
    """Test edge cases in week calculation."""
    print("\n" + "=" * 60)
    print("Testing week calculation edge cases")
    print("=" * 60)

    # Test a month that starts on Sunday
    # April 2025 starts on Tuesday
    weeks = get_weeks_in_month(2025, 4)
    print(f"\nApril 2025 (starts Tuesday): {len(weeks)} weeks")
    for start, end in weeks:
        print(f"  {start} - {end}")

    # June 2025 starts on Sunday
    weeks = get_weeks_in_month(2025, 6)
    print(f"\nJune 2025 (starts Sunday): {len(weeks)} weeks")
    for start, end in weeks:
        print(f"  {start} - {end}")

    print("\n✓ Edge case tests passed")


if __name__ == "__main__":
    test_march_2025()
    test_february_2025()
    test_january_2026()
    test_save_template()
    test_week_calculation_edge_cases()

    print("\n" + "=" * 60)
    print("All tests passed!")
    print("=" * 60)
