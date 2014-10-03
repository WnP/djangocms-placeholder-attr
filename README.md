# Django CMS Placeholder Attribute

# Description

`djangocms-placeholder-attr` allow you to call a plugin model attribute from a placeholder in [django-cms](https://github.com/divio/django-cms)

# Depends

- [django-cms](https://github.com/divio/django-cms)

# Installation
* use pip `pip install djangocms-placeholder-attr`
* Put in your INSTALLED_APPS: `INSTALLED_APPS += ('djangocms-placeholder-attr', )` 


# Usage

`cms_placeholder_attr` provide two tags `placeholder_attr` and `show_placeholder_attr` which are similar to django-cms `placeholder` and `show_placeholder` tags, but plugin model oriented.

- `placeholder_attr`

```django
{% placeholder_attr 'placeholder_name' 'plugin_model_class_name' 'model_attribute_name' %}
```

- `show_placeholder_attr`

```django
{% show_placeholder_attr 'placeholder_name' 'placeholder_id' 'plugin_model_class_name' 'model_attribute_name' %}
```

Be sure to have a placeholder named `placeholder_name` to use this plugin.

if you have a foreign key attribute you can use the following syntax: `my_fk_attribute.an_attribute_from_the_fk`
