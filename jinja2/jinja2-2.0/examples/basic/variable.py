from jinja2 import Template


print Template("""\
<html>
    Hello {{ user }}
</html>
""").render(user="jack")