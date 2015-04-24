from jinja2 import Template


print Template("""\
<html>
    {% if foo %}
        is foo
    {% else %}
        bar
    {% endif %}
</html>
""").render(foo = True)
