import re

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    """
    valid_username: Regex to validate username
    Args:
        username (data type: str): username
    Returns:
        return boolean True/False
    """
    return username and USER_RE.match(username)

PASSWORD_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    """
    valid_password: Regex to validate password
    Args:
        password (data type: str): password
    Returns:
        return boolean True/False
    """
    return password and PASSWORD_RE.match(password)


def match_password(password, verify_password):
    """
    match_password: function to confirm retyping password is same
    Args:
        password (data type: str): password
        verify_password (data type: str): retype password
    Returns:
        return boolean True/False
    """
    return password == verify_password


EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")
def valid_email(email):
    """
    valid_username: Regex to validate email
    Args:
        email (data type: str): email
    Returns:
        return boolean True/False
    """
    return not email or EMAIL_RE.match(email)

