import re

def validate_isbn(isbn):
    """
    Validate the correct format of an ISBN.
    """
    if not isbn:
        return False

    # Remove hyphens, spaces, and other characters
    clean_isbn = re.sub(r'[^0-9X]', '', isbn.upper())

    # Validate length (10 to 13 digits)
    if len(clean_isbn) == 10:
        return validate_isbn10(clean_isbn)
    elif len(clean_isbn) == 13:
        return validate_isbn13(clean_isbn)

    return False

def validate_isbn10(isbn):
    """
    Validate the correct format of an ISBN10.
    """
    if len(isbn) != 10:
        return False

    total = 0
    for i in range(9):
        if not isbn[i].isdigit():
            return False
        total += int(isbn[i]) * (10 - i)

    check_digit = isbn[9]
    if check_digit == 'X':
        total += 10
    elif check_digit.isdigit():
        total += int(check_digit)
    else:
        return False

    return total % 11 == 0

def validate_isbn13(isbn):
    """
    Validate the correct format of an ISBN13.
    """
    if len(isbn) != 13:
        return False

    if not isbn.isdigit():
        return False

    total = 0
    for i in range(12):
        multiplier = 1 if i % 2 == 0 else 3
        total += int(isbn[i]) * multiplier

    check_digit = (10 - (total % 10)) % 10
    return check_digit == int(isbn[12])
















