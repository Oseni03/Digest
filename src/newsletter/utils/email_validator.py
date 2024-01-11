from email_validator import validate_email, EmailNotValidError


def email_is_valid(email):
    try:
        # Check that the email address is valid. Turn on check_deliverability
        emailinfo = validate_email(email, check_deliverability=True)
        return True
    except EmailNotValidError as e:
        print(str(e))
        return False