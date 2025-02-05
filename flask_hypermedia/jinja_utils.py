from .resource import Link
from jinja2 import Environment, Undefined
from jinja2.runtime import Macro
from jinja2.filters import xmlattr
from jinja2.utils import pass_eval_context
from typing import Optional
from markupsafe import Markup, escape

@pass_eval_context
def link_to_a(eval_ctx, link: Link, *args, caller:Optional[Macro] = None, **kwargs):
    """
    Example (filter):

        {{ resource.links.next | link_to_a('Next', class='button') }}

    Example (call):

        {% call link_to_a(resource.links.next, class='Button') %}
            <img src='icons/next.png'/> Next
        {% endcall %}
    """
    if link is None or isinstance(link, Undefined):
        return ''
    if eval_ctx.autoescape:
        args = [escape(value) for value in args]
    if caller is not None:
        args.append(caller(link=link))
    # TODO kwargs as html attrs
    kwargs.setdefault('href', link.href)
    if 'rel' in kwargs:
        kwargs['rel'] = f"{link.rel} {kwargs['rel']}"
    else:
        kwargs['rel'] = link.rel
    result = f"<a{xmlattr(eval_ctx, kwargs)}>{' '.join(args)}</a>"
    return Markup(result) if eval_ctx.autoescape else result

# TODO
# def link_to_form()
# def link_to_link()
# templated links; could use https://github.com/std-uritemplate/std-uritemplate

def _install(env: Environment):
    # TODO better names?
    env.globals['link_to_a'] = link_to_a # For call syntax
    env.filters['link_to_a'] = link_to_a # For filter syntax