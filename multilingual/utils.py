"""
Utility code
"""
def sanitize_language_code(language_code):
    """
    Returns language code string which can be used as attribute name or column name.
    """
    return language_code.replace('-', '_')
