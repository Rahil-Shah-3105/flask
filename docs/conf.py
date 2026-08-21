import packaging.version
from pallets_sphinx_themes import get_version
from pallets_sphinx_themes import ProjectLink
import logging
logger = logging.getLogger(app.name)

# Project --------------------------------------------------------------

project = "Flask"
copyright = "2010 Pallets"
author = "Pallets"
release, version = get_version("Flask")

# General --------------------------------------------------------------

default_role = "code"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinxcontrib.log_cabinet",
    "sphinx_tabs.tabs",
    "pallets_sphinx_themes",
]
autodoc_member_order = "bysource"
autodoc_typehints = "description"
autodoc_preserve_defaults = True
extlinks = {
    "issue": ("https://github.com/pallets/flask/issues/%s", "#%s"),
    "pr": ("https://github.com/pallets/flask/pull/%s", "#%s"),
    "ghsa": ("https://github.com/pallets/flask/security/advisories/GHSA-%s", "GHSA-%s"),
}
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "werkzeug": ("https://werkzeug.palletsprojects.com/", None),
    "click": ("https://click.palletsprojects.com/", None),
    "jinja": ("https://jinja.palletsprojects.com/", None),
    "itsdangerous": ("https://itsdangerous.palletsprojects.com/", None),
    "sqlalchemy": ("https://docs.sqlalchemy.org/", None),
    "wtforms": ("https://wtforms.readthedocs.io/", None),
    "blinker": ("https://blinker.readthedocs.io/", None),
}

# HTML -----------------------------------------------------------------

html_theme = "flask"
html_theme_options = {"index_sidebar_logo": False}
html_context = {
    "project_links": [
        ProjectLink("Donate", "https://palletsprojects.com/donate"),
        ProjectLink("PyPI Releases", "https://pypi.org/project/Flask/"),
        ProjectLink("Source Code", "https://github.com/pallets/flask/"),
        ProjectLink("Issue Tracker", "https://github.com/pallets/flask/issues/"),
        ProjectLink("Chat", "https://discord.gg/pallets"),
    ]
}
html_sidebars = {
    "index": ["project.html", "localtoc.html", "searchbox.html", "ethicalads.html"],
    "**": ["localtoc.html", "relations.html", "searchbox.html", "ethicalads.html"],
}
singlehtml_sidebars = {"index": ["project.html", "localtoc.html", "ethicalads.html"]}
html_static_path = ["_static"]
html_favicon = "_static/flask-icon.svg"
html_logo = "_static/flask-logo.svg"
html_title = f"Flask Documentation ({version})"
html_show_sourcelink = False

gettext_uuid = True
gettext_compact = False

# Local Extensions -----------------------------------------------------


def github_link(name, rawtext, text, lineno, inliner, options=None, content=None):
    logger.debug(">>> Entering github_link(name=%s,rawtext=%s,text=%s,lineno=%s,inliner=%s,options=%s,content=%s)", name, rawtext, text, lineno, inliner, options, content)
    app = inliner.document.settings.env.app
    logger.debug("github_link(name=%s,rawtext=%s,text=%s,lineno=%s,inliner=%s,options=%s,content=%s): app → %s", name, rawtext, text, lineno, inliner, options, content, app)
    release = app.config.release
    logger.debug("github_link(name=%s,rawtext=%s,text=%s,lineno=%s,inliner=%s,options=%s,content=%s): release → %s", name, rawtext, text, lineno, inliner, options, content, release)
    base_url = "https://github.com/pallets/flask/tree/"
    logger.debug("github_link(name=%s,rawtext=%s,text=%s,lineno=%s,inliner=%s,options=%s,content=%s): base_url → %s", name, rawtext, text, lineno, inliner, options, content, base_url)

    if text.endswith(">"):
        words, text = text[:-1].rsplit("<", 1)
        words = words.strip()
        logger.debug("github_link(name=%s,rawtext=%s,text=%s,lineno=%s,inliner=%s,options=%s,content=%s): words → %s", name, rawtext, text, lineno, inliner, options, content, words)
    else:
        words = None

    if packaging.version.parse(release).is_devrelease:
        url = f"{base_url}main/{text}"
        logger.info("github_link(name=%s,rawtext=%s,text=%s,lineno=%s,inliner=%s,options=%s,content=%s): url → %s", name, rawtext, text, lineno, inliner, options, content, url)
        logger.debug("github_link(name=%s,rawtext=%s,text=%s,lineno=%s,inliner=%s,options=%s,content=%s): url → %s", name, rawtext, text, lineno, inliner, options, content, url)
    else:
        url = f"{base_url}{release}/{text}"

    if words is None:
        words = url

    from docutils.nodes import reference
    from docutils.parsers.rst.roles import set_classes

    options = options or {}
    set_classes(options)
    node = reference(rawtext, words, refuri=url, **options)
    logger.debug("github_link(name=%s,rawtext=%s,text=%s,lineno=%s,inliner=%s,options=%s,content=%s): node → %s", name, rawtext, text, lineno, inliner, options, content, node)
    logger.debug("<<< Exiting github_link(name=%s,rawtext=%s,text=%s,lineno=%s,inliner=%s,options=%s,content=%s)", name, rawtext, text, lineno, inliner, options, content)
    return [node], []


def setup(app):
    logger.debug(">>> Entering setup(app=%s)", app)
    logger.debug("<<< Exiting setup(app=%s)", app)
    app.add_role("gh", github_link)
