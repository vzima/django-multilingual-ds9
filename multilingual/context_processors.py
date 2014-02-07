"""
Multilingual context processor

Context variables:
  * ML_LANGUAGE - active language for multilingual usage
"""
from multilingual.languages import get_active


def multilingual(request):
    """
    Returns context variables containing information about available languages.
    """
    return {'ML_LANGUAGE': get_active()}
