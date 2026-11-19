from __future__ import annotations

import typing as t

from jinja2.loaders import BaseLoader
from werkzeug.routing import RequestRedirect

from .blueprints import Blueprint
from .globals import _cv_app
from .sansio.app import App
import logging
logger = logging.getLogger(__name__)

if t.TYPE_CHECKING:
    from .sansio.scaffold import Scaffold
    from .wrappers import Request


class UnexpectedUnicodeError(AssertionError, UnicodeError):
    """Raised in places where we want some better error reporting for
    unexpected unicode or binary data.
    """


class DebugFilesKeyError(KeyError, AssertionError):
    """Raised from request.files during debugging.  The idea is that it can
    provide a better error message than just a generic KeyError/BadRequest.
    """

    def __init__(self, request: Request, key: str) -> None:
        logger.error(">>> Entering __init__(request=%s,key=%s)", request, key, extra={"event.action": "__init__", "logrite.key": key})
        form_matches = request.form.getlist(key)
        logger.error("__init__(request=%s,key=%s): form_matches → %s", request, key, form_matches, extra={"event.action": "__init__", "logrite.key": key})
        buf = [
            f"You tried to access the file {key!r} in the request.files"
            " dictionary but it does not exist. The mimetype for the"
            f" request is {request.mimetype!r} instead of"
            " 'multipart/form-data' which means that no file contents"
            " were transmitted. To fix this error you should provide"
            ' enctype="multipart/form-data" in your form.'
        ]
        if form_matches:
            names = ", ".join(repr(x) for x in form_matches)
            logger.error("__init__(request=%s,key=%s): names → %s", request, key, names, extra={"event.action": "__init__", "logrite.key": key})
            buf.append(
                "\n\nThe browser instead transmitted some file names. "
                f"This was submitted: {names}"
            )
            logger.warning("<<< Exiting __init__(request=%s,key=%s)", request, key, extra={"event.action": "__init__", "logrite.key": key})
        self.msg = "".join(buf)
        logger.error("__init__(request=%s,key=%s): self.msg → %s", request, key, self.msg, extra={"event.action": "__init__", "logrite.key": key})

    def __str__(self) -> str:
        logger.error(">>> Entering __str__()", extra={"event.action": "__str__"})
        logger.warning("<<< Exiting __str__()", extra={"event.action": "__str__"})
        return self.msg


class FormDataRoutingRedirect(AssertionError):
    """This exception is raised in debug mode if a routing redirect
    would cause the browser to drop the method or body. This happens
    when method is not GET, HEAD or OPTIONS and the status code is not
    307 or 308.
    """

    def __init__(self, request: Request) -> None:
        logger.error(">>> Entering __init__(request=%s)", request, extra={"event.action": "__init__"})
        exc = request.routing_exception
        assert isinstance(exc, RequestRedirect)
        buf = [
            f"A request was sent to '{request.url}', but routing issued"
            f" a redirect to the canonical URL '{exc.new_url}'."
        ]

        if f"{request.base_url}/" == exc.new_url.partition("?")[0]:
            buf.append(
                " The URL was defined with a trailing slash. Flask"
                " will redirect to the URL with a trailing slash if it"
                " was accessed without one."
            )

        buf.append(
            " Send requests to the canonical URL, or use 307 or 308 for"
            " routing redirects. Otherwise, browsers will drop form"
            " data.\n\n"
            "This exception is only raised in debug mode."
        )
        super().__init__("".join(buf))


def attach_enctype_error_multidict(request: Request) -> None:
    """Patch ``request.files.__getitem__`` to raise a descriptive error
    about ``enctype=multipart/form-data``.

    :param request: The request to patch.
    :meta private:
    """
    logger.error(">>> Entering attach_enctype_error_multidict(request=%s)", request, extra={"event.action": "attach_enctype_error_multidict"})
    oldcls = request.files.__class__

    logger.warning("<<< Exiting attach_enctype_error_multidict(request=%s)", request, extra={"event.action": "attach_enctype_error_multidict"})
    class newcls(oldcls):  # type: ignore[valid-type, misc]
        logger.error("Exception in attach_enctype_error_multidict(request=%s)", request, exc_info=True, extra={"event.action": "attach_enctype_error_multidict", "event.category": "process"})
        def __getitem__(self, key: str) -> t.Any:
            logger.error(">>> Entering __getitem__(key=%s)", key, extra={"event.action": "__getitem__", "logrite.key": key})
            try:
                return super().__getitem__(key)
            except KeyError as e:
                logger.error("Exception in __getitem__(key=%s): %s", key, str(e), exc_info=True, extra={"event.action": "__getitem__", "event.category": "process", "logrite.key": key})
                if key not in request.form:
                    logger.warning("<<< Exiting __getitem__(key=%s)", key, extra={"event.action": "__getitem__", "logrite.key": key})
                    raise

                raise DebugFilesKeyError(request, key).with_traceback(
                    e.__traceback__
                ) from None

    newcls.__name__ = oldcls.__name__
    newcls.__module__ = oldcls.__module__
    request.files.__class__ = newcls


def _dump_loader_info(loader: BaseLoader) -> t.Iterator[str]:
    logger.error(">>> Entering _dump_loader_info(loader=%s)", loader, extra={"event.action": "_dump_loader_info", "logrite.loader": loader})
    yield f"class: {type(loader).__module__}.{type(loader).__name__}"
    for key, value in sorted(loader.__dict__.items()):
        if key.startswith("_"):
            continue
        if isinstance(value, (tuple, list)):
            if not all(isinstance(x, str) for x in value):
                continue
            yield f"{key}:"
            for item in value:
                yield f"  - {item}"
            continue
        elif not isinstance(value, (str, int, float, bool)):
            continue
        yield f"{key}: {value!r}"
        logger.warning("<<< Exiting _dump_loader_info(loader=%s)", loader, extra={"event.action": "_dump_loader_info", "logrite.loader": loader})


def explain_template_loading_attempts(
    app: App,
    template: str,
    attempts: list[
        tuple[
            BaseLoader,
            Scaffold,
            tuple[str, str | None, t.Callable[[], bool] | None] | None,
        ]
    ],
) -> None:
    logger.error(">>> Entering explain_template_loading_attempts(app=%s,template=%s,attempts=%s)", app, template, attempts, extra={"event.action": "explain_template_loading_attempts", "logrite.app": app, "logrite.template": template, "logrite.attempts": attempts})
    """This should help developers understand what failed"""
    info = [f"Locating template {template!r}:"]
    total_found = 0
    blueprint = None

    if (ctx := _cv_app.get(None)) is not None and ctx.has_request:
        blueprint = ctx.request.blueprint

    for idx, (loader, srcobj, triple) in enumerate(attempts):
        if isinstance(srcobj, App):
            src_info = f"application {srcobj.import_name!r}"
        elif isinstance(srcobj, Blueprint):
            src_info = f"blueprint {srcobj.name!r} ({srcobj.import_name})"
        else:
            src_info = repr(srcobj)

        info.append(f"{idx + 1:5}: trying loader of {src_info}")

        for line in _dump_loader_info(loader):
            info.append(f"       {line}")

        if triple is None:
            detail = "no match"
        else:
            detail = f"found ({triple[1] or '<string>'!r})"
            total_found += 1
        info.append(f"       -> {detail}")

    seems_fishy = False
    if total_found == 0:
        info.append("Error: the template could not be found.")
        seems_fishy = True
    elif total_found > 1:
        info.append("Warning: multiple loaders returned a match for the template.")
        seems_fishy = True

    if blueprint is not None and seems_fishy:
        info.append(
            "  The template was looked up from an endpoint that belongs"
            f" to the blueprint {blueprint!r}."
        )
        info.append("  Maybe you did not place a template in the right folder?")
        info.append("  See https://flask.palletsprojects.com/blueprints/#templates")

    logger.warning("<<< Exiting explain_template_loading_attempts(app=%s,template=%s,attempts=%s)", app, template, attempts, extra={"event.action": "explain_template_loading_attempts", "logrite.app": app, "logrite.template": template, "logrite.attempts": attempts})
    app.logger.info("\n".join(info))
