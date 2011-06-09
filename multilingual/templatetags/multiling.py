"""
Template tags provided by multilingual
"""
import re

from django import template
from multilingual import languages


register = template.Library()


class MlLockNode(template.Node):
    """
    Locks language and stores value in variable
    """
    def __init__(self, nodelist, language_code, varname=None):
        super(MlLockNode, self).__init__()
        self.nodelist = nodelist
        self.language_code = language_code
        self.varname = varname or 'ML_LANGUAGE'

    def render(self, context):
        # If language_code is string, strip quotes
        # otherwise resolve variable
        if self.language_code[0] == self.language_code[-1] and self.language_code[0] in ('"',"'"):
            language_code = self.language_code[1:-1]
        else:
            # Do not catch VariableDoesNotExist exception
            language_code = template.Variable(self.language_code).resolve(context)

        # Lock language, store code into context, render, restore context and release lock
        languages.lock(language_code)
        context.push()
        context[self.varname] = languages.get_active()
        output = self.nodelist.render(context)
        context.pop()
        languages.release()
        return output


def ml_lock(parser, token):
    """
    Locks multilingual language and stores its code into context.

    Examples::
        {% ml_lock 'cs' %}
            multilingual in czech ({{ ML_LANGUAGE }}) language
        {% endml_lock %}

        {% ml_lock language_code %}
            multilingual in {{ language_code }} language
        {% endml_lock %}

        {% ml_lock 'cs' as var1 %}
            multilingual in czech with code {{ var1 }}
        {% endml_lock %}
    """
    #TODO: rewrite this parsing in style of django.template.defaulttags.do_with or other tag
    try:
        tag_name, args = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires arguments" % token.contents.split()[0])
    #TODO: derived TokenParser might be better
    match = re.match(r'^(?P<language_code>[^ \t]*)([ \t]+as[ \t]+(?P<varname>\w+))?$', args)
    if match is None:
        raise template.TemplateSyntaxError("%r tag has incorrect arguments" % tag_name)
    language_code = match.groupdict()['language_code']
    varname = match.groupdict().get('varname')
    nodelist = parser.parse(('end%r' % tag_name,))
    parser.delete_first_token()
    return MlLockNode(nodelist, language_code, varname)


# {% ml_lock 'cs' %}multilingual in czech ({{ ML_LANGUAGE }}) language{% endml_lock %}
# {% ml_lock language_code %}multilingual in {{ language_code }} language{% endml_lock %}
# {% ml_lock language_code as var1 %}Language_code stored in {{ var1 }}{% endml_lock %}
register.tag('ml_lock', ml_lock)
