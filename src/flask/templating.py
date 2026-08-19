from __future__ import annotations

import typing as t

from jinja2 import BaseLoader
from jinja2 import Environment as BaseEnvironment
from jinja2 import Template
from jinja2 import TemplateNotFound

from .ctx import AppContext
from .globals import app_ctx
from .helpers import stream_with_context
from .signals import before_render_template
from .signals import template_rendered

if t.TYPE_CHECKING:  # pragma: no cover
    from .sansio.app import App
    from .sansio.scaffold import Scaffold
    import logging
logger = logging.getLogger(app.name)


def _default_template_ctx_processor() -> dict[str, t.Any]:
    """Default template context processor.  Replaces the ``request`` and ``g``
    proxies with their concrete objects for faster access.
    """
    logger.debug(">>> Entering _default_template_ctx_processor()")
    ctx = app_ctx._get_current_object()
    logger.debug("_default_template_ctx_processor(): ctx → %s", ctx)
    rv: dict[str, t.Any] = {"g": ctx.g}

    if ctx.has_request:
        rv["request"] = ctx.request
        # The session proxy cannot be replaced, accessing it gets
        # RequestContext.session, which sets session.accessed.

    logger.debug("<<< Exiting _default_template_ctx_processor()")
    return rv


class Environment(BaseEnvironment):
    """Works like a regular Jinja environment but has some additional
    knowledge of how Flask's blueprint works so that it can prepend the
    name of the blueprint to referenced templates if necessary.
    """

    def __init__(self, app: App, **options: t.Any) -> None:
        logger.debug(">>> Entering __init__(app=%s)", app)
        if "loader" not in options:
            options["loader"] = app.create_global_jinja_loader()
        BaseEnvironment.__init__(self, **options)
        logger.debug("<<< Exiting __init__(app=%s)", app)
        self.app = app
        logger.debug("__init__(self=%s,app=%s): self.app → %s", self, app, self.app)


class DispatchingJinjaLoader(BaseLoader):
    """A loader that looks for templates in the application and all
    the blueprint folders.
    """

    def __init__(self, app: App) -> None:
        self.app = app

    def get_source(
        self, environment: BaseEnvironment, template: str
    ) -> tuple[str, str | None, t.Callable[[], bool] | None]:
        if self.app.config["EXPLAIN_TEMPLATE_LOADING"]:
            return self._get_source_explained(environment, template)
        return self._get_source_fast(environment, template)

    def _get_source_explained(
        self, environment: BaseEnvironment, template: str
    ) -> tuple[str, str | None, t.Callable[[], bool] | None]:
        attempts = []
        rv: tuple[str, str | None, t.Callable[[], bool] | None] | None
        trv: None | (tuple[str, str | None, t.Callable[[], bool] | None]) = None

        for srcobj, loader in self._iter_loaders(template):
            try:
                rv = loader.get_source(environment, template)
                if trv is None:
                    trv = rv
            except TemplateNotFound:
                rv = None
            attempts.append((loader, srcobj, rv))

        from .debughelpers import explain_template_loading_attempts

        explain_template_loading_attempts(self.app, template, attempts)

        if trv is not None:
            return trv
        raise TemplateNotFound(template)

    def _get_source_fast(
        self, environment: BaseEnvironment, template: str
    ) -> tuple[str, str | None, t.Callable[[], bool] | None]:
        for _srcobj, loader in self._iter_loaders(template):
            try:
                return loader.get_source(environment, template)
            except TemplateNotFound:
                continue
        raise TemplateNotFound(template)

    def _iter_loaders(self, template: str) -> t.Iterator[tuple[Scaffold, BaseLoader]]:
        logger.debug(">>> Entering _iter_loaders(template=%s)", template)
        loader = self.app.jinja_loader
        logger.debug("_iter_loaders(self=%s,template=%s): loader → %s", self, template, loader)
        if loader is not None:
            yield self.app, loader

        for blueprint in self.app.iter_blueprints():
            loader = blueprint.jinja_loader
            if loader is not None:
                yield blueprint, loader
                logger.debug("<<< Exiting _iter_loaders(template=%s)", template)

    def list_templates(self) -> list[str]:
        logger.debug(">>> Entering list_templates()")
        result = set()
        logger.debug("list_templates(): result → %s", result)
        loader = self.app.jinja_loader
        logger.debug("list_templates(self=%s): loader → %s", self, loader)
        if loader is not None:
            result.update(loader.list_templates())

        for blueprint in self.app.iter_blueprints():
            loader = blueprint.jinja_loader
            if loader is not None:
                for template in loader.list_templates():
                    result.add(template)

        logger.debug("<<< Exiting list_templates()")
        return list(result)


def _render(ctx: AppContext, template: Template, context: dict[str, t.Any]) -> str:
    logger.debug(">>> Entering _render(ctx=%s,template=%s,context=%s)", ctx, template, context)
    app = ctx.app
    logger.debug("_render(ctx=%s,template=%s,context=%s): app → %s", ctx, template, context, app)
    app.update_template_context(ctx, context)
    before_render_template.send(
        app, _async_wrapper=app.ensure_sync, template=template, context=context
    )
    rv = template.render(context)
    logger.debug("_render(ctx=%s,template=%s,context=%s): rv → %s", ctx, template, context, rv)
    template_rendered.send(
        app, _async_wrapper=app.ensure_sync, template=template, context=context
    )
    logger.debug("<<< Exiting _render(ctx=%s,template=%s,context=%s)", ctx, template, context)
    return rv


def render_template(
    template_name_or_list: str | Template | list[str | Template],
    **context: t.Any,
) -> str:
    """Render a template by name with the given context.

    :param template_name_or_list: The name of the template to render. If
        a list is given, the first name to exist will be rendered.
    :param context: The variables to make available in the template.
    """
    ctx = app_ctx._get_current_object()
    template = ctx.app.jinja_env.get_or_select_template(template_name_or_list)
    return _render(ctx, template, context)


def render_template_string(source: str, **context: t.Any) -> str:
    """Render a template from the given source string with the given
    context.

    :param source: The source code of the template to render.
    :param context: The variables to make available in the template.
    """
    logger.debug(">>> Entering render_template_string(source=%s)", source)
    ctx = app_ctx._get_current_object()
    logger.debug("render_template_string(source=%s): ctx → %s", source, ctx)
    template = ctx.app.jinja_env.from_string(source)
    logger.debug("render_template_string(source=%s): template → %s", source, template)
    logger.debug("<<< Exiting render_template_string(source=%s)", source)
    return _render(ctx, template, context)


def _stream(
    ctx: AppContext, template: Template, context: dict[str, t.Any]
) -> t.Iterator[str]:
    app = ctx.app
    app.update_template_context(ctx, context)
    before_render_template.send(
        app, _async_wrapper=app.ensure_sync, template=template, context=context
    )

    def generate() -> t.Iterator[str]:
        logger.debug(">>> Entering generate()")
        yield from template.generate(context)
        template_rendered.send(
            app, _async_wrapper=app.ensure_sync, template=template, context=context
        )
        logger.debug("<<< Exiting generate()")

    return stream_with_context(generate())


def stream_template(
    template_name_or_list: str | Template | list[str | Template],
    **context: t.Any,
) -> t.Iterator[str]:
    """Render a template by name with the given context as a stream.
    This returns an iterator of strings, which can be used as a
    streaming response from a view.

    :param template_name_or_list: The name of the template to render. If
        a list is given, the first name to exist will be rendered.
    :param context: The variables to make available in the template.

    .. versionadded:: 2.2
    """
    ctx = app_ctx._get_current_object()
    template = ctx.app.jinja_env.get_or_select_template(template_name_or_list)
    return _stream(ctx, template, context)


def stream_template_string(source: str, **context: t.Any) -> t.Iterator[str]:
    """Render a template from the given source string with the given
    context as a stream. This returns an iterator of strings, which can
    be used as a streaming response from a view.

    :param source: The source code of the template to render.
    :param context: The variables to make available in the template.

    .. versionadded:: 2.2
    """
    logger.debug(">>> Entering stream_template_string(source=%s)", source)
    ctx = app_ctx._get_current_object()
    logger.debug("stream_template_string(source=%s): ctx → %s", source, ctx)
    template = ctx.app.jinja_env.from_string(source)
    logger.debug("stream_template_string(source=%s): template → %s", source, template)
    logger.debug("<<< Exiting stream_template_string(source=%s)", source)
    return _stream(ctx, template, context)
