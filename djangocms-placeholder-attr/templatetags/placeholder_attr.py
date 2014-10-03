from django import template
from django.conf import settings
from django.core.cache import cache
from django.utils.safestring import mark_safe
from sekizai.helpers import Watcher
from classytags.core import Options, Tag
from classytags.arguments import Argument, MultiValueArgument
from classytags.helpers import InclusionTag
from cms.utils import get_language_from_request, get_cms_setting
try:
    from cms.utils.compat.type_checks import string_types
except ImportError, e:
    from django.utils.six import string_types
#from cms.models import Placeholder as PlaceholderModel
from cms.templatetags.cms_tags import (
    PlaceholderOptions,
    _get_placeholder,
    get_site_id,
    _get_cache_key,
    _clean_key,
    restore_sekizai_context as _restore_sekizai,
    _get_page_by_untyped_arg,
)
from cms.utils.placeholder import validate_placeholder_name


register = template.Library()


def get_plugins(placeholder):
    for key in placeholder.__dict__:
        if '_plugins_cache' in key:
            return getattr(placeholder, key)
    return False


def resolve_plugin(plugins, plugin_class_name):
    for plugin in plugins:
        if plugin.__class__.__name__ == plugin_class_name:
            return plugin
    return False


def resolve_attr(plugin, plugin_attr):
    res = plugin
    for attr in plugin_attr.split('.'):
        res = getattr(res, attr)
    return res


def get_placholder_attr(placeholder, name, plugin_class_name, plugin_attr):
    plugins = get_plugins(placeholder)
    if not plugins:
        #if settings.DEBUG:
        #    raise Exception('No plugin set for Placeholder %s' % (name,))
        return ''

    plugin = resolve_plugin(plugins, plugin_class_name)
    if not plugin:
        if settings.DEBUG:
            raise Exception(
                'Class %s not found in Placeholder %s plugins' % (
                    plugin_class_name, name))
        return ''

    res = resolve_attr(plugin, plugin_attr)

    return res


class PlaceholderAttr(Tag):
    name = 'placeholder_attr'
    options = PlaceholderOptions(
        Argument('name', resolve=False),
        Argument('plugin_class_name', resolve=False),
        Argument('plugin_attr', resolve=False),
        MultiValueArgument('extra_bits', required=False, resolve=False),
        blocks=[
            ('endplaceholder', 'nodelist'),
        ]
    )

    def render_tag(
            self, context,
            name, plugin_class_name, plugin_attr,
            extra_bits, nodelist=None):
        validate_placeholder_name(name)
        width = None
        for bit in extra_bits:
            if bit == 'inherit':
                pass
            elif bit.isdigit():
                width = int(bit)
                import warnings

                warnings.warn(
                    "The width parameter for the placeholder " +
                    "tag is deprecated.",
                    DeprecationWarning
                )
        if not 'request' in context:
            return ''
        request = context['request']
        if width:
            context.update({'width': width})

        page = request.current_page
        if not page or page == 'dummy':
            if nodelist:
                return nodelist.render(context)

            return ''

        placeholder = _get_placeholder(page, page, context, name)

        res = get_placholder_attr(
            placeholder, name, plugin_class_name, plugin_attr)

        return res

register.tag(PlaceholderAttr)


def _show_placeholder_attr_for_page(
        context, placeholder_name,
        plugin_class_name, plugin_attr,
        page_lookup, lang=None,
        site=None, cache_result=True):

    validate_placeholder_name(placeholder_name)

    request = context.get('request', False)
    site_id = get_site_id(site)

    if not request:
        return {'content': ''}
    if lang is None:
        lang = get_language_from_request(request)

    if cache_result:
        base_key = _get_cache_key(
            '_show_placeholder_for_page', page_lookup, lang, site_id)

        cache_key = _clean_key(
            '%s_placeholder:%s' % (
                base_key, placeholder_name
            )) + plugin_class_name + '.' + plugin_attr

        cached_value = cache.get(cache_key)
        if isinstance(cached_value, dict):  # new style
            _restore_sekizai(context, cached_value['sekizai'])
            return {'content': mark_safe(cached_value['content'])}
        elif isinstance(cached_value, string_types):  # old style
            return {'content': mark_safe(cached_value)}

    page = _get_page_by_untyped_arg(page_lookup, request, site_id)
    if not page:
        return {'content': ''}
    watcher = Watcher(context)

    placeholder = _get_placeholder(page, page, context, placeholder_name)
    content = get_placholder_attr(
        placeholder, placeholder_name, plugin_class_name, plugin_attr)

    changes = watcher.get_changes()

    if cache_result:
        cache.set(
            cache_key,
            {
                'content': content,
                'sekizai': changes
            }, get_cms_setting('CACHE_DURATIONS')['content'])

    if content:
        return {'content': mark_safe(content)}

    return {'content': ''}


class ShowPlaceholderAttr(InclusionTag):
    template = 'cms/content.html'
    name = 'show_placeholder_attr'

    options = Options(
        Argument('placeholder_name'),
        Argument('reverse_id'),
        Argument('plugin_class_name', resolve=False),
        Argument('plugin_attr', resolve=False),
        Argument('lang', required=False, default=None),
        Argument('site', required=False, default=None),
    )

    def get_context(self, *args, **kwargs):
        return _show_placeholder_attr_for_page(
            **self.get_kwargs(*args, **kwargs))

    def get_kwargs(
            self, context, placeholder_name,
            plugin_class_name, plugin_attr,
            reverse_id, lang, site):
        cache_result = True
        if 'preview' in context['request'].GET:
            cache_result = False
        return {
            'context': context,
            'placeholder_name': placeholder_name,
            'plugin_class_name': plugin_class_name,
            'plugin_attr': plugin_attr,
            'page_lookup': reverse_id,
            'lang': lang,
            'site': site,
            'cache_result': cache_result
        }

register.tag(ShowPlaceholderAttr)