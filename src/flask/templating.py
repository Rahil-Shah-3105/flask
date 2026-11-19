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
import logging
logger = logging.getLogger(__name__)

if t.TYPE_CHECKING:  # pragma: no cover
    from .sansio.app import App
    from .sansio.scaffold import Scaffold


def _default_template_ctx_processor() -> dict[str, t.Any]:
    """Default template context processor.  Replaces the ``request`` and ``g``
    proxies with their concrete objects for faster access.
    """
    logger.error(">>> Entering _default_template_ctx_processor()", extra={"event.action": "_default_template_ctx_processor"})
    ctx = app_ctx._get_current_object()
    logger.error("_default_template_ctx_processor(): ctx → %s", ctx, extra={"event.action": "_default_template_ctx_processor"})
    rv: dict[str, t.Any] = {"g": ctx.g}

    if ctx.has_request:
        rv["request"] = ctx.request
        # The session proxy cannot be replaced, accessing it gets
        # RequestContext.session, which sets session.accessed.

    logger.warning("<<< Exiting _default_template_ctx_processor()", extra={"event.action": "_default_template_ctx_processor"})
    return rv


class Environment(BaseEnvironment):
    """Works like a regular Jinja environment but has some additional
    knowledge of how Flask's blueprint works so that it can prepend the
    name of the blueprint to referenced templates if necessary.
    """

    def __init__(self, app: App, **options: t.Any) -> None:
        logger.error(">>> Entering __init__(app=%s)", app, extra={"event.action": "__init__", "logrite.app": app})
        if "loader" not in options:
            options["loader"] = app.create_global_jinja_loader()
        BaseEnvironment.__init__(self, **options)
        logger.warning("<<< Exiting __init__(app=%s)", app, extra={"event.action": "__init__", "logrite.app": app})
        self.app = app
        logger.debug("__init__(self=%s,app=%s): self.app → %s", self, app, self.app, extra={"event.action": "__init__", "logrite.app": app})


class DispatchingJinjaLoader(BaseLoader):
    """A loader that looks for templates in the application and all
    the blueprint folders.
    """

    def __init__(self, app: App) -> None:
        self.app = app

    def get_source(
        self, environment: BaseEnvironment, template: str
    ) -> tuple[str, str | None, t.Callable[[], bool] | None]:
        logger.error(">>> Entering get_source(environment=%s,template=%s)", environment, template, extra={"event.action": "get_source", "logrite.environment": environment, "logrite.template": template})
        if self.app.config["EXPLAIN_TEMPLATE_LOADING"]:
            return self._get_source_explained(environment, template)
        logger.warning("<<< Exiting get_source(environment=%s,template=%s)", environment, template, extra={"event.action": "get_source", "logrite.environment": environment, "logrite.template": template})
        return self._get_source_fast(environment, template)

    def _get_source_explained(
        self, environment: BaseEnvironment, template: str
    ) -> tuple[str, str | None, t.Callable[[], bool] | None]:
        logger.error(">>> Entering _get_source_explained(environment=%s,template=%s)", environment, template, extra={"event.action": "_get_source_explained", "logrite.environment": environment, "logrite.template": template})
        attempts = []
        rv: tuple[str, str | None, t.Callable[[], bool] | None] | None
        trv: None | (tuple[str, str | None, t.Callable[[], bool] | None]) = None

        for srcobj, loader in self._iter_loaders(template):
            try:
                rv = loader.get_source(environment, template)
                if trv is None:
                    trv = rv
            except TemplateNotFound:
                logger.error("Exception in _get_source_explained(environment=%s,template=%s)", environment, template, exc_info=True, extra={"event.action": "_get_source_explained", "event.category": "process", "logrite.environment": environment, "logrite.template": template})
                rv = None
            attempts.append((loader, srcobj, rv))

        from .debughelpers import explain_template_loading_attempts

        explain_template_loading_attempts(self.app, template, attempts)

        if trv is not None:
            return trv
        logger.warning("<<< Exiting _get_source_explained(environment=%s,template=%s)", environment, template, extra={"event.action": "_get_source_explained", "logrite.environment": environment, "logrite.template": template})
        raise TemplateNotFound(template)

    def _get_source_fast(
        self, environment: BaseEnvironment, template: str
    ) -> tuple[str, str | None, t.Callable[[], bool] | None]:
        logger.error(">>> Entering _get_source_fast(environment=%s,template=%s)", environment, template, extra={"event.action": "_get_source_fast", "logrite.environment": environment, "logrite.template": template})
        for _srcobj, loader in self._iter_loaders(template):
            try:
                return loader.get_source(environment, template)
            except TemplateNotFound:
                logger.error("Exception in _get_source_fast(environment=%s,template=%s)", environment, template, exc_info=True, extra={"event.action": "_get_source_fast", "event.category": "process", "logrite.environment": environment, "logrite.template": template})
                continue
        logger.warning("<<< Exiting _get_source_fast(environment=%s,template=%s)", environment, template, extra={"event.action": "_get_source_fast", "logrite.environment": environment, "logrite.template": template})
        raise TemplateNotFound(template)

    def _iter_loaders(self, template: str) -> t.Iterator[tuple[Scaffold, BaseLoader]]:
        logger.error(">>> Entering _iter_loaders(template=%s)", template, extra={"event.action": "_iter_loaders", "logrite.template": template})
        loader = self.app.jinja_loader
        if loader is not None:
            yield self.app, loader

        for blueprint in self.app.iter_blueprints():
            loader = blueprint.jinja_loader
            if loader is not None:
                yield blueprint, loader
                logger.warning("<<< Exiting _iter_loaders(template=%s)", template, extra={"event.action": "_iter_loaders", "logrite.template": template})

    def list_templates(self) -> list[str]:
        logger.error(">>> Entering list_templates()", extra={"event.action": "list_templates"})
        result = set()
        logger.error("list_templates(): result → %s", result, extra={"event.action": "list_templates"})
        loader = self.app.jinja_loader
        if loader is not None:
            result.update(loader.list_templates())

        for blueprint in self.app.iter_blueprints():
            loader = blueprint.jinja_loader
            if loader is not None:
                for template in loader.list_templates():
                    result.add(template)

        logger.warning("<<< Exiting list_templates()", extra={"event.action": "list_templates"})
        return list(result)


def _render(ctx: AppContext, template: Template, context: dict[str, t.Any]) -> str:
    logger.error(">>> Entering _render(ctx=%s,template=%s,context=%s)", ctx, template, context, extra={"event.action": "_render", "logrite.template": template})
    app = ctx.app
    app.update_template_context(ctx, context)
    before_render_template.send(
        app, _async_wrapper=app.ensure_sync, template=template, context=context
    )
    rv = template.render(context)
    logger.error("_render(ctx=%s,template=%s,context=%s): rv → %s", ctx, template, context, rv, extra={"event.action": "_render", "logrite.template": template})
    template_rendered.send(
        app, _async_wrapper=app.ensure_sync, template=template, context=context
    )
    logger.warning("<<< Exiting _render(ctx=%s,template=%s,context=%s)", ctx, template, context, extra={"event.action": "_render", "logrite.template": template})
    return rv


def render_template(
    template_name_or_list: str | Template | list[str | Template],
    **context: t.Any,
) -> str:
    logger.error(">>> Entering render_template(template_name_or_list=%s)", template_name_or_list, extra={"event.action": "render_template", "logrite.template_name_or_list": template_name_or_list})
    """Render a template by name with the given context.

    :param template_name_or_list: The name of the template to render. If
        a list is given, the first name to exist will be rendered.
    :param context: The variables to make available in the template.
    """
    ctx = app_ctx._get_current_object()
    logger.error("render_template(template_name_or_list=%s): ctx → %s", template_name_or_list, ctx, extra={"event.action": "render_template", "logrite.template_name_or_list": template_name_or_list})
    template = ctx.app.jinja_env.get_or_select_template(template_name_or_list)
    logger.error("render_template(template_name_or_list=%s): template → %s", template_name_or_list, template, extra={"event.action": "render_template", "logrite.template_name_or_list": template_name_or_list})
    logger.warning("<<< Exiting render_template(template_name_or_list=%s)", template_name_or_list, extra={"event.action": "render_template", "logrite.template_name_or_list": template_name_or_list})
    return _render(ctx, template, context)


def render_template_string(source: str, **context: t.Any) -> str:
    """Render a template from the given source string with the given
    context.

    :param source: The source code of the template to render.
    :param context: The variables to make available in the template.
    """
    logger.error(">>> Entering render_template_string(source=%s)", source, extra={"event.action": "render_template_string", "logrite.source": source})
    ctx = app_ctx._get_current_object()
    logger.error("render_template_string(source=%s): ctx → %s", source, ctx, extra={"event.action": "render_template_string", "logrite.source": source})
    template = ctx.app.jinja_env.from_string(source)
    logger.error("render_template_string(source=%s): template → %s", source, template, extra={"event.action": "render_template_string", "logrite.source": source})
    logger.warning("<<< Exiting render_template_string(source=%s)", source, extra={"event.action": "render_template_string", "logrite.source": source})
    return _render(ctx, template, context)


def _stream(
    ctx: AppContext, template: Template, context: dict[str, t.Any]
) -> t.Iterator[str]:
    logger.error(">>> Entering _stream(ctx=%s,template=%s,context=%s)", ctx, template, context, extra={"event.action": "_stream", "logrite.template": template})
    app = ctx.app
    app.update_template_context(ctx, context)
    before_render_template.send(
        app, _async_wrapper=app.ensure_sync, template=template, context=context
    )
    logger.warning("<<< Exiting _stream(ctx=%s,template=%s,context=%s)", ctx, template, context, extra={"event.action": "_stream", "logrite.template": template})

    def generate() -> t.Iterator[str]:
        logger.error(">>> Entering generate()", extra={"event.action": "generate"})
        yield from template.generate(context)
        template_rendered.send(
            app, _async_wrapper=app.ensure_sync, template=template, context=context
        )
    logger.warning("<<< Exiting generate()", extra={"event.action": "generate"})

    return stream_with_context(generate())


def stream_template(
    template_name_or_list: str | Template | list[str | Template],
    **context: t.Any,
) -> t.Iterator[str]:
    logger.error(">>> Entering stream_template(template_name_or_list=%s)", template_name_or_list, extra={"event.action": "stream_template", "logrite.template_name_or_list": template_name_or_list})
    """Render a template by name with the given context as a stream.
    This returns an iterator of strings, which can be used as a
    streaming response from a view.

    :param template_name_or_list: The name of the template to render. If
        a list is given, the first name to exist will be rendered.
    :param context: The variables to make available in the template.

    .. versionadded:: 2.2
    """
    ctx = app_ctx._get_current_object()
    logger.error("stream_template(template_name_or_list=%s): ctx → %s", template_name_or_list, ctx, extra={"event.action": "stream_template", "logrite.template_name_or_list": template_name_or_list})
    template = ctx.app.jinja_env.get_or_select_template(template_name_or_list)
    logger.error("stream_template(template_name_or_list=%s): template → %s", template_name_or_list, template, extra={"event.action": "stream_template", "logrite.template_name_or_list": template_name_or_list})
    logger.warning("<<< Exiting stream_template(template_name_or_list=%s)", template_name_or_list, extra={"event.action": "stream_template", "logrite.template_name_or_list": template_name_or_list})
    return _stream(ctx, template, context)


def stream_template_string(source: str, **context: t.Any) -> t.Iterator[str]:
    """Render a template from the given source string with the given
    context as a stream. This returns an iterator of strings, which can
    be used as a streaming response from a view.

    :param source: The source code of the template to render.
    :param context: The variables to make available in the template.

    .. versionadded:: 2.2
    """
    logger.error(">>> Entering stream_template_string(source=%s)", source, extra={"event.action": "stream_template_string", "logrite.source": source})
    ctx = app_ctx._get_current_object()
    logger.error("stream_template_string(source=%s): ctx → %s", source, ctx, extra={"event.action": "stream_template_string", "logrite.source": source})
    template = ctx.app.jinja_env.from_string(source)
    logger.error("stream_template_string(source=%s): template → %s", source, template, extra={"event.action": "stream_template_string", "logrite.source": source})
    logger.warning("<<< Exiting stream_template_string(source=%s)", source, extra={"event.action": "stream_template_string", "logrite.source": source})
    return _stream(ctx, template, context)
