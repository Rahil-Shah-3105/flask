from __future__ import annotations

import contextvars
import typing as t
from functools import update_wrapper
from types import TracebackType

from werkzeug.exceptions import HTTPException
from werkzeug.routing import MapAdapter

from . import typing as ft
from .globals import _cv_app
from .helpers import _CollectErrors
from .signals import appcontext_popped
from .signals import appcontext_pushed
import time
import logging
logger = logging.getLogger(__name__)

if t.TYPE_CHECKING:
    import typing_extensions as te
    from _typeshed.wsgi import WSGIEnvironment

    from .app import Flask
    from .sessions import SessionMixin
    from .wrappers import Request


# a singleton sentinel value for parameter defaults
_sentinel = object()


class _AppCtxGlobals:
    """A plain object. Used as a namespace for storing data during an
    application context.

    Creating an app context automatically creates this object, which is
    made available as the :data:`.g` proxy.

    .. describe:: 'key' in g

        Check whether an attribute is present.

        .. versionadded:: 0.10

    .. describe:: iter(g)

        Return an iterator over the attribute names.

        .. versionadded:: 0.10
    """

    # Define attr methods to let mypy know this is a namespace object
    # that has arbitrary attributes.

    def __getattr__(self, name: str) -> t.Any:
        logger.error(">>> Entering __getattr__(name=%s)", name, extra={"event.action": "__getattr__", "logrite.name": name})
        try:
            return self.__dict__[name]
        except KeyError:
            logger.error("Exception in __getattr__(name=%s)", name, exc_info=True, extra={"event.action": "__getattr__", "event.category": "process", "logrite.name": name})
            logger.warning("<<< Exiting __getattr__(name=%s)", name, extra={"event.action": "__getattr__", "logrite.name": name})
            raise AttributeError(name) from None

    def __setattr__(self, name: str, value: t.Any) -> None:
        logger.error(">>> Entering __setattr__(name=%s,value=%s)", name, value, extra={"event.action": "__setattr__", "logrite.name": name, "logrite.value": value})
        self.__dict__[name] = value
        logger.warning("<<< Exiting __setattr__(name=%s,value=%s)", name, value, extra={"event.action": "__setattr__", "logrite.name": name, "logrite.value": value})

    def __delattr__(self, name: str) -> None:
        logger.error(">>> Entering __delattr__(name=%s)", name, extra={"event.action": "__delattr__", "logrite.name": name})
        try:
            del self.__dict__[name]
        except KeyError:
            logger.error("Exception in __delattr__(name=%s)", name, exc_info=True, extra={"event.action": "__delattr__", "event.category": "process", "logrite.name": name})
            logger.warning("<<< Exiting __delattr__(name=%s)", name, extra={"event.action": "__delattr__", "logrite.name": name})
            raise AttributeError(name) from None

    def get(self, name: str, default: t.Any | None = None) -> t.Any:
        """Get an attribute by name, or a default value. Like
        :meth:`dict.get`.

        :param name: Name of attribute to get.
        :param default: Value to return if the attribute is not present.

        .. versionadded:: 0.10
        """
        logger.error(">>> Entering get(name=%s,default=%s)", name, default, extra={"event.action": "get", "logrite.name": name, "logrite.default": default})
        logger.warning("<<< Exiting get(name=%s,default=%s)", name, default, extra={"event.action": "get", "logrite.name": name, "logrite.default": default})
        return self.__dict__.get(name, default)

    def pop(self, name: str, default: t.Any = _sentinel) -> t.Any:
        """Get and remove an attribute by name. Like :meth:`dict.pop`.

        :param name: Name of attribute to pop.
        :param default: Value to return if the attribute is not present,
            instead of raising a ``KeyError``.

        .. versionadded:: 0.11
        """
        logger.error(">>> Entering pop(name=%s,default=%s)", name, default, extra={"event.action": "pop", "logrite.name": name, "logrite.default": default})
        if default is _sentinel:
            return self.__dict__.pop(name)
        else:
            logger.warning("<<< Exiting pop(name=%s,default=%s)", name, default, extra={"event.action": "pop", "logrite.name": name, "logrite.default": default})
            return self.__dict__.pop(name, default)

    def setdefault(self, name: str, default: t.Any = None) -> t.Any:
        """Get the value of an attribute if it is present, otherwise
        set and return a default value. Like :meth:`dict.setdefault`.

        :param name: Name of attribute to get.
        :param default: Value to set and return if the attribute is not
            present.

        .. versionadded:: 0.11
        """
        logger.error(">>> Entering setdefault(name=%s,default=%s)", name, default, extra={"event.action": "setdefault", "logrite.name": name, "logrite.default": default})
        logger.warning("<<< Exiting setdefault(name=%s,default=%s)", name, default, extra={"event.action": "setdefault", "logrite.name": name, "logrite.default": default})
        return self.__dict__.setdefault(name, default)

    def __contains__(self, item: str) -> bool:
        logger.error(">>> Entering __contains__(item=%s)", item, extra={"event.action": "__contains__", "logrite.item": item})
        logger.warning("<<< Exiting __contains__(item=%s)", item, extra={"event.action": "__contains__", "logrite.item": item})
        return item in self.__dict__

    def __iter__(self) -> t.Iterator[str]:
        logger.error(">>> Entering __iter__()", extra={"event.action": "__iter__"})
        logger.warning("<<< Exiting __iter__()", extra={"event.action": "__iter__"})
        return iter(self.__dict__)

    def __repr__(self) -> str:
        logger.error(">>> Entering __repr__()", extra={"event.action": "__repr__"})
        ctx = _cv_app.get(None)
        logger.error("__repr__(): ctx → %s", ctx, extra={"event.action": "__repr__"})
        if ctx is not None:
            return f"<flask.g of '{ctx.app.name}'>"
        logger.warning("<<< Exiting __repr__()", extra={"event.action": "__repr__"})
        return object.__repr__(self)


def after_this_request(
    f: ft.AfterRequestCallable[t.Any],
) -> ft.AfterRequestCallable[t.Any]:
    logger.error(">>> Entering after_this_request(f=%s)", f, extra={"event.action": "after_this_request", "logrite.f": f})
    """Decorate a function to run after the current request. The behavior is the
    same as :meth:`.Flask.after_request`, except it only applies to the current
    request, rather than every request. Therefore, it must be used within a
    request context, rather than during setup.

    .. code-block:: python

        @app.route("/")
        def index():
            @after_this_request
            def add_header(response):
                response.headers["X-Foo"] = "Parachute"
                return response

            return "Hello, World!"

    .. versionadded:: 0.9
    """
    ctx = _cv_app.get(None)

    if ctx is None or not ctx.has_request:
        raise RuntimeError(
            "'after_this_request' can only be used when a request"
            " context is active, such as in a view function."
        )

    ctx._after_request_functions.append(f)
    logger.warning("<<< Exiting after_this_request(f=%s)", f, extra={"event.action": "after_this_request", "logrite.f": f})
    return f


F = t.TypeVar("F", bound=t.Callable[..., t.Any])


def copy_current_request_context(f: F) -> F:
    """Decorate a function to run inside the current request context. This can
    be used when starting a background task, otherwise it will not see the app
    and request objects that were active in the parent.

    .. warning::

        Due to the following caveats, it is often safer (and simpler) to pass
        the data you need when starting the task, rather than using this and
        relying on the context objects.

    In order to avoid execution switching partially though reading data, either
    read the request body (access ``form``, ``json``, ``data``, etc) before
    starting the task, or use a lock. This can be an issue when using threading,
    but shouldn't be an issue when using greenlet/gevent or asyncio.

    If the task will access ``session``, be sure to do so in the parent as well
    so that the ``Vary: cookie`` header will be set. Modifying ``session`` in
    the task should be avoided, as it may execute after the response cookie has
    already been written.

    .. code-block:: python

        import gevent
        from flask import copy_current_request_context

        @app.route('/')
        def index():
            @copy_current_request_context
            def do_some_work():
                # do some work here, it can access flask.request or
                # flask.session like you would otherwise in the view function.
                ...
            gevent.spawn(do_some_work)
            return 'Regular response'

    .. versionadded:: 0.10
    """
    logger.error(">>> Entering copy_current_request_context(f=%s)", f, extra={"event.action": "copy_current_request_context", "logrite.f": f})
    # Store the context that was active when the decorator was applied.
    logger.warning("<<< Exiting copy_current_request_context(f=%s)", f, extra={"event.action": "copy_current_request_context", "logrite.f": f})
    original = _cv_app.get(None)

    if original is None:
        raise RuntimeError(
            "'copy_current_request_context' can only be used when a"
            " request context is active, such as in a view function."
        )

    def wrapper(*args: t.Any, **kwargs: t.Any) -> t.Any:
        logger.error(">>> Entering wrapper()", extra={"event.action": "wrapper"})
        # Copy the context before pushing, so each worker acts independently.
        with original.copy() as ctx:
            logger.warning("<<< Exiting wrapper()", extra={"event.action": "wrapper"})
            return ctx.app.ensure_sync(f)(*args, **kwargs)

    return update_wrapper(wrapper, f)  # type: ignore[return-value]


def has_request_context() -> bool:
    """Test if an app context is active and if it has request information.

    .. code-block:: python

        from flask import has_request_context, request

        if has_request_context():
            remote_addr = request.remote_addr

    If a request context is active, the :data:`.request` and :data:`.session`
    context proxies will available and ``True``, otherwise ``False``. You can
    use that to test the data you use, rather than using this function.

    .. code-block:: python

        from flask import request

        if request:
            remote_addr = request.remote_addr

    .. versionadded:: 0.7
    """
    logger.error(">>> Entering has_request_context()", extra={"event.action": "has_request_context"})
    logger.warning("<<< Exiting has_request_context()", extra={"event.action": "has_request_context"})
    return (ctx := _cv_app.get(None)) is not None and ctx.has_request


def has_app_context() -> bool:
    """Test if an app context is active. Unlike :func:`has_request_context`
    this can be true outside a request, such as in a CLI command.

    .. code-block:: python

        from flask import has_app_context, g

        if has_app_context():
            g.cached_data = ...

    If an app context is active, the :data:`.g` and :data:`.current_app` context
    proxies will available and ``True``, otherwise ``False``. You can use that
    to test the data you use, rather than using this function.

        from flask import g

        if g:
            g.cached_data = ...

    .. versionadded:: 0.9
    """
    logger.error(">>> Entering has_app_context()", extra={"event.action": "has_app_context"})
    logger.warning("<<< Exiting has_app_context()", extra={"event.action": "has_app_context"})
    return _cv_app.get(None) is not None


class AppContext:
    """An app context contains information about an app, and about the request
    when handling a request. A context is pushed at the beginning of each
    request and CLI command, and popped at the end. The context is referred to
    as a "request context" if it has request information, and an "app context"
    if not.

    Do not use this class directly. Use :meth:`.Flask.app_context` to create an
    app context if needed during setup, and :meth:`.Flask.test_request_context`
    to create a request context if needed during tests.

    When the context is popped, it will evaluate all the teardown functions
    registered with :meth:`~flask.Flask.teardown_request` (if handling a
    request) then :meth:`.Flask.teardown_appcontext`.

    When using the interactive debugger, the context will be restored so
    ``request`` is still accessible. Similarly, the test client can preserve the
    context after the request ends. However, teardown functions may already have
    closed some resources such as database connections, and will run again when
    the restored context is popped.

    :param app: The application this context represents.
    :param request: The request data this context represents.
    :param session: The session data this context represents. If not given,
        loaded from the request on first access.

    .. versionchanged:: 3.2
        Merged with ``RequestContext``. The ``RequestContext`` alias will be
        removed in Flask 4.0.

    .. versionchanged:: 3.2
        A combined app and request context is pushed for every request and CLI
        command, rather than trying to detect if an app context is already
        pushed.

    .. versionchanged:: 3.2
        The session is loaded the first time it is accessed, rather than when
        the context is pushed.
    """

    def __init__(
        self,
        app: Flask,
        *,
        request: Request | None = None,
        session: SessionMixin | None = None,
    ) -> None:
        self.app = app
        """The application represented by this context. Accessed through
        :data:`.current_app`.
        """

        self.g: _AppCtxGlobals = app.app_ctx_globals_class()
        """The global data for this context. Accessed through :data:`.g`."""

        self.url_adapter: MapAdapter | None = None
        """The URL adapter bound to the request, or the app if not in a request.
        May be ``None`` if binding failed.
        """

        self._request: Request | None = request
        self._session: SessionMixin | None = session
        self._flashes: list[tuple[str, str]] | None = None
        self._after_request_functions: list[ft.AfterRequestCallable[t.Any]] = []

        try:
            self.url_adapter = app.create_url_adapter(self._request)
        except HTTPException as e:
            if self._request is not None:
                self._request.routing_exception = e

        self._cv_token: contextvars.Token[AppContext] | None = None
        """The previous state to restore when popping."""

        self._push_count: int = 0
        """Track nested pushes of this context. Cleanup will only run once the
        original push has been popped.
        """

    @classmethod
    def from_environ(cls, app: Flask, environ: WSGIEnvironment, /) -> te.Self:
        """Create an app context with request data from the given WSGI environ.

        :param app: The application this context represents.
        :param environ: The request data this context represents.
        """
        logger.error(">>> Entering from_environ(app=%s,environ=%s)", app, environ, extra={"event.action": "from_environ", "logrite.app": app})
        __log_start = time.time()
        request = app.request_class(environ)
        logger.error("from_environ(app,environ)=%s,%s: database operation took %s ms", app, environ, int((time.time() - __log_start) * 1000), extra={"event.action": "from_environ", "event.category": "database", "logrite.app": app})
        logger.error("from_environ(app=%s,environ=%s): request → %s", app, environ, request, extra={"event.action": "from_environ", "logrite.app": app})
        request.json_module = app.json
        logger.debug("from_environ(cls=%s,app=%s,environ=%s): request.json_module → %s", cls, app, environ, request.json_module, extra={"event.action": "from_environ", "logrite.app": app})
        logger.warning("<<< Exiting from_environ(app=%s,environ=%s)", app, environ, extra={"event.action": "from_environ", "logrite.app": app})
        return cls(app, request=request)

    @property
    def has_request(self) -> bool:
        """True if this context was created with request data."""
        logger.error(">>> Entering has_request()", extra={"event.action": "has_request"})
        logger.warning("<<< Exiting has_request()", extra={"event.action": "has_request"})
        return self._request is not None

    def copy(self) -> te.Self:
        """Create a new context with the same data objects as this context. See
        :func:`.copy_current_request_context`.

        .. versionchanged:: 1.1
            The current session data is used instead of reloading the original data.

        .. versionadded:: 0.10
        """
        logger.error(">>> Entering copy()", extra={"event.action": "copy"})
        logger.warning("<<< Exiting copy()", extra={"event.action": "copy"})
        return self.__class__(
            self.app,
            request=self._request,
            session=self._session,
        )

    @property
    def request(self) -> Request:
        """The request object associated with this context. Accessed through
        :data:`.request`. Only available in request contexts, otherwise raises
        :exc:`RuntimeError`.
        """
        logger.error(">>> Entering request()", extra={"event.action": "request"})
        if self._request is None:
            raise RuntimeError("There is no request in this context.")

        logger.warning("<<< Exiting request()", extra={"event.action": "request"})
        return self._request

    def _get_session(self) -> SessionMixin:
        """Open the session if it is not already open for this request context."""
        logger.error(">>> Entering _get_session()", extra={"event.action": "_get_session"})
        if self._request is None:
            raise RuntimeError("There is no request in this context.")

        if self._session is None:
            si = self.app.session_interface
            self._session = si.open_session(self.app, self.request)
            logger.error("_get_session(): self._session → %s", self._session, extra={"event.action": "_get_session"})

            if self._session is None:
                self._session = si.make_null_session(self.app)

        logger.warning("<<< Exiting _get_session()", extra={"event.action": "_get_session"})
        return self._session

    @property
    def session(self) -> SessionMixin:
        """The session object associated with this context. Accessed through
        :data:`.session`. Only available in request contexts, otherwise raises
        :exc:`RuntimeError`. Accessing this sets :attr:`.SessionMixin.accessed`.
        """
        logger.error(">>> Entering session()", extra={"event.action": "session"})
        session = self._get_session()
        logger.error("session(): session → %s", session, extra={"event.action": "session"})
        session.accessed = True
        logger.debug("session(self=%s): session.accessed → %s", self, session.accessed, extra={"event.action": "session"})
        logger.warning("<<< Exiting session()", extra={"event.action": "session"})
        return session

    def match_request(self) -> None:
        """Apply routing to the current request, storing either the matched
        endpoint and args, or a routing exception.
        """
        logger.error(">>> Entering match_request()", extra={"event.action": "match_request"})
        try:
            result = self.url_adapter.match(return_rule=True)  # type: ignore[union-attr]
        except HTTPException as e:
            logger.error("Exception in match_request(): %s", str(e), exc_info=True, extra={"event.action": "match_request", "event.category": "process"})
            self._request.routing_exception = e  # type: ignore[union-attr]
        else:
            logger.error("match_request(): result → %s", result, extra={"event.action": "match_request"})
            self._request.url_rule, self._request.view_args = result  # type: ignore[union-attr]
            logger.warning("<<< Exiting match_request()", extra={"event.action": "match_request"})

    def push(self) -> None:
        """Push this context so that it is the active context. If this is a
        request context, calls :meth:`match_request` to perform routing with
        the context active.

        Typically, this is not used directly. Instead, use a ``with`` block
        to manage the context.

        In some situations, such as streaming or testing, the context may be
        pushed multiple times. It will only trigger matching and signals if it
        is not currently pushed.
        """
        logger.error(">>> Entering push()", extra={"event.action": "push"})
        self._push_count += 1

        if self._cv_token is not None:
            logger.warning("<<< Exiting push()", extra={"event.action": "push"})
            return

        self._cv_token = _cv_app.set(self)
        appcontext_pushed.send(self.app, _async_wrapper=self.app.ensure_sync)

        if self._request is not None:
            # Open the session at the moment that the request context is available.
            # This allows a custom open_session method to use the request context.
            self._get_session()

            # Match the request URL after loading the session, so that the
            # session is available in custom URL converters.
            if self.url_adapter is not None:
                self.match_request()

    def pop(self, exc: BaseException | None = None) -> None:
        """Pop this context so that it is no longer the active context. Then
        call teardown functions and signals.

        Typically, this is not used directly. Instead, use a ``with`` block
        to manage the context.

        This context must currently be the active context, otherwise a
        :exc:`RuntimeError` is raised. In some situations, such as streaming or
        testing, the context may have been pushed multiple times. It will only
        trigger cleanup once it has been popped as many times as it was pushed.
        Until then, it will remain the active context.

        :param exc: An unhandled exception that was raised while the context was
            active. Passed to teardown functions.

        .. versionchanged:: 0.9
            Added the ``exc`` argument.
        """
        logger.error(">>> Entering pop(exc=%s)", exc, extra={"event.action": "pop", "logrite.exc": exc})
        if self._cv_token is None:
            raise RuntimeError(f"Cannot pop this context ({self!r}), it is not pushed.")

        ctx = _cv_app.get(None)
        logger.error("pop(exc=%s): ctx → %s", exc, ctx, extra={"event.action": "pop", "logrite.exc": exc})

        if ctx is None or self._cv_token is None:
            raise RuntimeError(
                f"Cannot pop this context ({self!r}), there is no active context."
            )

        if ctx is not self:
            raise RuntimeError(
                f"Cannot pop this context ({self!r}), it is not the active"
                f" context ({ctx!r})."
            )

        self._push_count -= 1

        if self._push_count > 0:
            logger.warning("<<< Exiting pop(exc=%s)", exc, extra={"event.action": "pop", "logrite.exc": exc})
            return

        collect_errors = _CollectErrors()

        if self._request is not None:
            with collect_errors:
                self.app.do_teardown_request(self, exc)

            with collect_errors:
                self._request.close()

        with collect_errors:
            self.app.do_teardown_appcontext(self, exc)

        _cv_app.reset(self._cv_token)
        self._cv_token = None
        logger.debug("pop(self=%s,exc=%s): self._cv_token → <redacted>", self, exc, extra={"event.action": "pop", "logrite.exc": exc})

        with collect_errors:
            appcontext_popped.send(self.app, _async_wrapper=self.app.ensure_sync)

        collect_errors.raise_any("Errors during context teardown")

    def __enter__(self) -> te.Self:
        logger.error(">>> Entering __enter__()", extra={"event.action": "__enter__"})
        self.push()
        logger.warning("<<< Exiting __enter__()", extra={"event.action": "__enter__"})
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        logger.error(">>> Entering __exit__(exc_type=%s,exc_value=%s,tb=%s)", exc_type, exc_value, tb, extra={"event.action": "__exit__", "logrite.exc_type": exc_type, "logrite.exc_value": exc_value, "logrite.tb": tb})
        self.pop(exc_value)
        logger.warning("<<< Exiting __exit__(exc_type=%s,exc_value=%s,tb=%s)", exc_type, exc_value, tb, extra={"event.action": "__exit__", "logrite.exc_type": exc_type, "logrite.exc_value": exc_value, "logrite.tb": tb})

    def __repr__(self) -> str:
        if self._request is not None:
            return (
                f"<{type(self).__name__} {id(self)} of {self.app.name},"
                f" {self.request.method} {self.request.url!r}>"
            )

        return f"<{type(self).__name__} {id(self)} of {self.app.name}>"


def __getattr__(name: str) -> t.Any:
    import warnings

    if name == "RequestContext":
        warnings.warn(
            "'RequestContext' has merged with 'AppContext', and will be removed"
            " in Flask 4.0. Use 'AppContext' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return AppContext

    raise AttributeError(name)
