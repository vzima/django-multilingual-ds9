import re

from django import template
from multilingual import languages


register = template.Library()


class LanguageLockNode(template.Node):
    def __init__(self, nodelist, language_code, varname=None):
        self.nodelist = nodelist
        self.language_code = language_code
        self.varname = varname or 'active_language'

    def render(self, context):
        if self.language_code[0] == self.language_code[-1] and self.language_code[0] in ('"',"'"):
            language_code = self.language_code[1:-1]
        else:
            # Do not catch VariableDoesNotExist exception
            language_code = template.Variable(self.language_code).resolve(context)
        languages.lock(language_code)
        context[self.varname] = languages.get_active()
        output = self.nodelist.render(context)
        languages.release()
        context[self.varname] = languages.get_active()
        return output


def language_lock(parser, token):
    try:
        tag_name, args = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires arguments" % token.contents.split()[0])
    #TODO: derived TokenParser might be better
    match = re.match(r'^(?P<language_code>[^ \t]*)([ \t]+as[ \t]+(?P<varname>\w+))?$', '"huhu"  as  huhla')
    if match is None:
        raise template.TemplateSyntaxError("%r tag has incorrect arguments" % tag_name)
    language_code = match.groupdict()['language_code']
    varname = match.groupdict().get('varname')
    nodelist = parser.parse(('end%r' % tag_name,))
    parser.delete_first_token()
    return LanguageLockNode(nodelist, language_code, varname)


# {% lang_lock 'cs' %}multilingual in czech{% endlang_lock %}
# {% lang_lock language_code %}multilingual in language_code language{% endlang_lock %}
# {% lang_lock language_code as active_language %}Language_code stored in {{active_language}}{% endlang_lock %}
register.tag('lang_lock', language_lock)
