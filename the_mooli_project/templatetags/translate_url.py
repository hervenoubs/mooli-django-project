# mooli_app/templatetags/translate_url.py
from django.template import Library
from django.urls import translate_url
register = Library()

@register.simple_tag(takes_context=True)
def translate_url(context, lang_code):
    path = context['request'].path
    return translate_url(path, lang_code)