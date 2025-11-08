"""
Simple script to reset is_printed field
Save as: reset_printed.py

Usage:
    python manage.py shell -c "from reset_printed import reset; reset()"
"""

from summitPage.models import Registrant


def reset():
    """Reset all is_printed to NULL"""
    count = Registrant.objects.all().update(is_printed=None)
    print(f"✅ Reset {count} registrants to NULL")
    return count


def set_all_printed():
    """Set all is_printed to 1"""
    count = Registrant.objects.all().update(is_printed=1)
    print(f"✅ Set {count} registrants to PRINTED (1)")
    return count


def check():
    """Check current status"""
    total = Registrant.objects.count()
    printed = Registrant.objects.filter(is_printed=1).count()
    null = Registrant.objects.filter(is_printed__isnull=True).count()

    print(f"Total: {total}")
    print(f"Printed (1): {printed}")
    print(f"NULL: {null}")

    return {'total': total, 'printed': printed, 'null': null}