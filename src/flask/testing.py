from __future__ import annotations

import importlib.metadata
import typing as t
from contextlib import contextmanager
from contextlib import ExitStack
from copy import copy
from types import TracebackType
from urllib.parse import urlsplit

import werkzeug.test
from click.testing import CliRunner
from click.testing import Result
from werkzeug.test import Client
from werkzeug.wrappers import Request as BaseRequest

from .cli import ScriptInfo
from .sessions import SessionMixin
import logging
logger = logging.getLogger(__name__)

if t.TYPE_CHECKING:  # pragma: no cover
    from _typeshed.wsgi import WSGIEnvironment
    from werkzeug.test import TestResponse

    from .app import Flask


class EnvironBuilder(werkzeug.test.EnvironBuilder):
    """An :class:`~werkzeug.test.EnvironBuilder`, that takes defaults from the
    application.

    :param app: The Flask application to configure the environment from.
    :param path: URL path being requested.
    :param base_url: Base URL where the app is being served, which
        ``path`` is relative to. If not given, built from
        :data:`PREFERRED_URL_SCHEME`, ``subdomain``,
        :data:`SERVER_NAME`, and :data:`APPLICATION_ROOT`.
    :param subdomain: Subdomain name to append to :data:`SERVER_NAME`.
    :param url_scheme: Scheme to use instead of
        :data:`PREFERRED_URL_SCHEME`.
    :param json: If given, this is serialized as JSON and passed as
        ``data``. Also defaults ``content_type`` to
        ``application/json``.
    :param args: other positional arguments passed to
        :class:`~werkzeug.test.EnvironBuilder`.
    :param kwargs: other keyword arguments passed to
        :class:`~werkzeug.test.EnvironBuilder`.
    """

    def __init__(
        self,
        app: Flask,
        path: str = "/",
        base_url: str | None = None,
        subdomain: str | None = None,
        url_scheme: str | None = None,
        *args: t.Any,
        **kwargs: t.Any,
    ) -> None:
        logger.error(">>> Entering __init__(app=%s,path=%s,base_url=%s,subdomain=%s,url_scheme=%s)", app, path, base_url, subdomain, url_scheme, extra={"event.action": "__init__", "logrite.app": app, "logrite.path": path, "logrite.base_url": base_url, "logrite.subdomain": subdomain, "logrite.url_scheme": url_scheme})
        assert not (base_url or subdomain or url_scheme) or (
            base_url is not None
        ) != bool(subdomain or url_scheme), (
            'Cannot pass "subdomain" or "url_scheme" with "base_url".'
        )

        if base_url is None:
            http_host = app.config.get("SERVER_NAME") or "localhost"
            logger.error("__init__(app=%s,path=%s,base_url=%s,subdomain=%s,url_scheme=%s): http_host → %s", app, path, base_url, subdomain, url_scheme, http_host, extra={"event.action": "__init__", "logrite.app": app, "logrite.path": path, "logrite.base_url": base_url, "logrite.subdomain": subdomain, "logrite.url_scheme": url_scheme})
            app_root = app.config["APPLICATION_ROOT"]
            logger.error("__init__(app=%s,path=%s,base_url=%s,subdomain=%s,url_scheme=%s): app_root → %s", app, path, base_url, subdomain, url_scheme, app_root, extra={"event.action": "__init__", "logrite.app": app, "logrite.path": path, "logrite.base_url": base_url, "logrite.subdomain": subdomain, "logrite.url_scheme": url_scheme})

            if subdomain:
                http_host = f"{subdomain}.{http_host}"

            if url_scheme is None:
                url_scheme = app.config["PREFERRED_URL_SCHEME"]
                logger.error("__init__(app=%s,path=%s,base_url=%s,subdomain=%s,url_scheme=%s): url_scheme → %s", app, path, base_url, subdomain, url_scheme, url_scheme, extra={"event.action": "__init__", "logrite.app": app, "logrite.path": path, "logrite.base_url": base_url, "logrite.subdomain": subdomain, "logrite.url_scheme": url_scheme})

            url = urlsplit(path)
            logger.error("__init__(app=%s,path=%s,base_url=%s,subdomain=%s,url_scheme=%s): url → %s", app, path, base_url, subdomain, url_scheme, url, extra={"event.action": "__init__", "logrite.app": app, "logrite.path": path, "logrite.base_url": base_url, "logrite.subdomain": subdomain, "logrite.url_scheme": url_scheme})
            base_url = (
                f"{url.scheme or url_scheme}://{url.netloc or http_host}"
                f"/{app_root.lstrip('/')}"
            )
            path = url.path
            logger.error("__init__(app=%s,path=%s,base_url=%s,subdomain=%s,url_scheme=%s): path → %s", app, path, base_url, subdomain, url_scheme, path, extra={"event.action": "__init__", "logrite.app": app, "logrite.path": path, "logrite.base_url": base_url, "logrite.subdomain": subdomain, "logrite.url_scheme": url_scheme})

            if url.query:
                path = f"{path}?{url.query}"

        self.app = app
        super().__init__(path, base_url, *args, **kwargs)
        logger.debug("__init__(self=%s,app=%s,path=%s,base_url=%s,subdomain=%s,url_scheme=%s): self.app → %s", self, app, path, base_url, subdomain, url_scheme, self.app, extra={"event.action": "__init__", "logrite.app": app, "logrite.path": path, "logrite.base_url": base_url, "logrite.subdomain": subdomain, "logrite.url_scheme": url_scheme})
        logger.warning("<<< Exiting __init__(app=%s,path=%s,base_url=%s,subdomain=%s,url_scheme=%s)", app, path, base_url, subdomain, url_scheme, extra={"event.action": "__init__", "logrite.app": app, "logrite.path": path, "logrite.base_url": base_url, "logrite.subdomain": subdomain, "logrite.url_scheme": url_scheme})

    def json_dumps(self, obj: t.Any, **kwargs: t.Any) -> str:
        """Serialize ``obj`` to a JSON-formatted string.

        The serialization will be configured according to the config associated
        with this EnvironBuilder's ``app``.
        """
        logger.error(">>> Entering json_dumps(obj=%s)", obj, extra={"event.action": "json_dumps", "logrite.obj": obj})
        logger.warning("<<< Exiting json_dumps(obj=%s)", obj, extra={"event.action": "json_dumps", "logrite.obj": obj})
        return self.app.json.dumps(obj, **kwargs)


_werkzeug_version = ""


def _get_werkzeug_version() -> str:
    logger.error(">>> Entering _get_werkzeug_version()", extra={"event.action": "_get_werkzeug_version"})
    global _werkzeug_version

    if not _werkzeug_version:
        _werkzeug_version = importlib.metadata.version("werkzeug")
    logger.error("_get_werkzeug_version(): _werkzeug_version → %s", _werkzeug_version, extra={"event.action": "_get_werkzeug_version"})

    logger.warning("<<< Exiting _get_werkzeug_version()", extra={"event.action": "_get_werkzeug_version"})
    return _werkzeug_version


class FlaskClient(Client):
    """Works like a regular Werkzeug test client, with additional behavior for
    Flask. Can defer the cleanup of the request context until the end of a
    ``with`` block. For general information about how to use this class refer to
    :class:`werkzeug.test.Client`.

    .. versionchanged:: 0.12
       `app.test_client()` includes preset default environment, which can be
       set after instantiation of the `app.test_client()` object in
       `client.environ_base`.

    Basic usage is outlined in the :doc:`/testing` chapter.
    """

    application: Flask

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        super().__init__(*args, **kwargs)
        logger.error(">>> Entering __init__()", extra={"event.action": "__init__"})
        self.preserve_context = False
        logger.debug("__init__(self=%s): self.preserve_context → %s", self, self.preserve_context, extra={"event.action": "__init__"})
        self._new_contexts: list[t.ContextManager[t.Any]] = []
        logger.warning("<<< Exiting __init__()", extra={"event.action": "__init__"})
        self._context_stack = ExitStack()
        logger.error("__init__(): self._context_stack → %s", self._context_stack, extra={"event.action": "__init__"})
        self.environ_base = {
            "REMOTE_ADDR": "127.0.0.1",
            "HTTP_USER_AGENT": f"Werkzeug/{_get_werkzeug_version()}",
        }
        logger.debug("__init__(self=%s): self.environ_base → %s", self, self.environ_base, extra={"event.action": "__init__"})

    @contextmanager
    def session_transaction(
        self, *args: t.Any, **kwargs: t.Any
    ) -> t.Iterator[SessionMixin]:
        logger.error(">>> Entering session_transaction()", extra={"event.action": "session_transaction"})
        """When used in combination with a ``with`` statement this opens a
        session transaction.  This can be used to modify the session that
        the test client uses.  Once the ``with`` block is left the session is
        stored back.

        ::

            with client.session_transaction() as session:
                session['value'] = 42

        Internally this is implemented by going through a temporary test
        request context and since session handling could depend on
        request variables this function accepts the same arguments as
        :meth:`~flask.Flask.test_request_context` which are directly
        passed through.
        """
        if self._cookies is None:
            raise TypeError(
                "Cookies are disabled. Create a client with 'use_cookies=True'."
            )

        app = self.application
        ctx = app.test_request_context(*args, **kwargs)
        logger.error("session_transaction(): ctx → %s", ctx, extra={"event.action": "session_transaction"})
        self._add_cookies_to_wsgi(ctx.request.environ)

        with ctx:
            sess = app.session_interface.open_session(app, ctx.request)
            logger.error("session_transaction(): sess → %s", sess, extra={"event.action": "session_transaction"})

        if sess is None:
            raise RuntimeError("Session backend did not open a session.")

        yield sess
        resp = app.response_class()
        logger.error("session_transaction(): resp → %s", resp, extra={"event.action": "session_transaction"})

        if app.session_interface.is_null_session(sess):
            logger.warning("<<< Exiting session_transaction()", extra={"event.action": "session_transaction"})
            return

        with ctx:
            app.session_interface.save_session(app, sess, resp)

        self._update_cookies_from_response(
            urlsplit(ctx.request.host_url).hostname or "localhost",
            ctx.request.path,
            resp.headers.getlist("Set-Cookie"),
        )

    def _copy_environ(self, other: WSGIEnvironment) -> WSGIEnvironment:
        logger.error(">>> Entering _copy_environ(other=%s)", other, extra={"event.action": "_copy_environ", "logrite.other": other})
        out = {**self.environ_base, **other}

        if self.preserve_context:
            out["werkzeug.debug.preserve_context"] = self._new_contexts.append

        logger.warning("<<< Exiting _copy_environ(other=%s)", other, extra={"event.action": "_copy_environ", "logrite.other": other})
        return out

    def _request_from_builder_args(
        self, args: tuple[t.Any, ...], kwargs: dict[str, t.Any]
    ) -> BaseRequest:
        logger.error(">>> Entering _request_from_builder_args(args=%s,kwargs=%s)", args, kwargs, extra={"event.action": "_request_from_builder_args"})
        kwargs["environ_base"] = self._copy_environ(kwargs.get("environ_base", {}))
        builder = EnvironBuilder(self.application, *args, **kwargs)
        logger.error("_request_from_builder_args(args=%s,kwargs=%s): builder → %s", args, kwargs, builder, extra={"event.action": "_request_from_builder_args"})

        try:
            return builder.get_request()
        finally:
            logger.warning("<<< Exiting _request_from_builder_args(args=%s,kwargs=%s)", args, kwargs, extra={"event.action": "_request_from_builder_args"})
            builder.close()

    def open(
        self,
        *args: t.Any,
        buffered: bool = False,
        follow_redirects: bool = False,
        **kwargs: t.Any,
    ) -> TestResponse:
        logger.error(">>> Entering open(buffered=%s,follow_redirects=%s)", buffered, follow_redirects, extra={"event.action": "open", "logrite.buffered": buffered, "logrite.follow_redirects": follow_redirects})
        if args and isinstance(
            args[0], (werkzeug.test.EnvironBuilder, dict, BaseRequest)
        ):
            if isinstance(args[0], werkzeug.test.EnvironBuilder):
                builder = copy(args[0])
                logger.error("open(buffered=%s,follow_redirects=%s): builder → %s", buffered, follow_redirects, builder, extra={"event.action": "open", "logrite.buffered": buffered, "logrite.follow_redirects": follow_redirects})
                builder.environ_base = self._copy_environ(builder.environ_base or {})  # type: ignore[arg-type]
                request = builder.get_request()
            elif isinstance(args[0], dict):
                request = EnvironBuilder.from_environ(
                    args[0], app=self.application, environ_base=self._copy_environ({})
                ).get_request()
                logger.error("open(buffered=%s,follow_redirects=%s): request → %s", buffered, follow_redirects, request, extra={"event.action": "open", "logrite.buffered": buffered, "logrite.follow_redirects": follow_redirects})
            else:
                # isinstance(args[0], BaseRequest)
                request = copy(args[0])
                request.environ = self._copy_environ(request.environ)
        else:
            # request is None
            request = self._request_from_builder_args(args, kwargs)

        # Pop any previously preserved contexts. This prevents contexts
        # from being preserved across redirects or multiple requests
        # within a single block.
        self._context_stack.close()

        response = super().open(
            request,
            buffered=buffered,
            follow_redirects=follow_redirects,
        )
        logger.error("open(buffered=%s,follow_redirects=%s): response → %s", buffered, follow_redirects, response, extra={"event.action": "open", "logrite.buffered": buffered, "logrite.follow_redirects": follow_redirects})
        response.json_module = self.application.json  # type: ignore[assignment]
        logger.debug("open(self=%s,buffered=%s,follow_redirects=%s): response.json_module → %s", self, buffered, follow_redirects, response.json_module, extra={"event.action": "open", "logrite.buffered": buffered, "logrite.follow_redirects": follow_redirects})

        # Re-push contexts that were preserved during the request.
        for cm in self._new_contexts:
            self._context_stack.enter_context(cm)

        self._new_contexts.clear()
        logger.warning("<<< Exiting open(buffered=%s,follow_redirects=%s)", buffered, follow_redirects, extra={"event.action": "open", "logrite.buffered": buffered, "logrite.follow_redirects": follow_redirects})
        return response

    def __enter__(self) -> FlaskClient:
        logger.error(">>> Entering __enter__()", extra={"event.action": "__enter__"})
        if self.preserve_context:
            raise RuntimeError("Cannot nest client invocations")
        self.preserve_context = True
        logger.debug("__enter__(self=%s): self.preserve_context → %s", self, self.preserve_context, extra={"event.action": "__enter__"})
        logger.warning("<<< Exiting __enter__()", extra={"event.action": "__enter__"})
        return self

    def __exit__(
        self,
        exc_type: type | None,
        exc_value: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        logger.error(">>> Entering __exit__(exc_type=%s,exc_value=%s,tb=%s)", exc_type, exc_value, tb, extra={"event.action": "__exit__", "logrite.exc_type": exc_type, "logrite.exc_value": exc_value, "logrite.tb": tb})
        self.preserve_context = False
        logger.debug("__exit__(self=%s,exc_type=%s,exc_value=%s,tb=%s): self.preserve_context → %s", self, exc_type, exc_value, tb, self.preserve_context, extra={"event.action": "__exit__", "logrite.exc_type": exc_type, "logrite.exc_value": exc_value, "logrite.tb": tb})
        self._context_stack.close()
        logger.warning("<<< Exiting __exit__(exc_type=%s,exc_value=%s,tb=%s)", exc_type, exc_value, tb, extra={"event.action": "__exit__", "logrite.exc_type": exc_type, "logrite.exc_value": exc_value, "logrite.tb": tb})


class FlaskCliRunner(CliRunner):
    """A :class:`~click.testing.CliRunner` for testing a Flask app's
    CLI commands. Typically created using
    :meth:`~flask.Flask.test_cli_runner`. See :ref:`testing-cli`.
    """

    def __init__(self, app: Flask, **kwargs: t.Any) -> None:
        logger.error(">>> Entering __init__(app=%s)", app, extra={"event.action": "__init__", "logrite.app": app})
        self.app = app
        super().__init__(**kwargs)
        logger.debug("__init__(self=%s,app=%s): self.app → %s", self, app, self.app, extra={"event.action": "__init__", "logrite.app": app})
        logger.warning("<<< Exiting __init__(app=%s)", app, extra={"event.action": "__init__", "logrite.app": app})

    def invoke(  # type: ignore
        self, cli: t.Any = None, args: t.Any = None, **kwargs: t.Any
    ) -> Result:
        logger.error(">>> Entering invoke(cli=%s,args=%s)", cli, args, extra={"event.action": "invoke", "logrite.cli": cli})
        """Invokes a CLI command in an isolated environment. See
        :meth:`CliRunner.invoke <click.testing.CliRunner.invoke>` for
        full method documentation. See :ref:`testing-cli` for examples.

        If the ``obj`` argument is not given, passes an instance of
        :class:`~flask.cli.ScriptInfo` that knows how to load the Flask
        app being tested.

        :param cli: Command object to invoke. Default is the app's
            :attr:`~flask.app.Flask.cli` group.
        :param args: List of strings to invoke the command with.

        :return: a :class:`~click.testing.Result` object.
        """
        if cli is None:
            cli = self.app.cli

        if "obj" not in kwargs:
            kwargs["obj"] = ScriptInfo(create_app=lambda: self.app)

        logger.warning("<<< Exiting invoke(cli=%s,args=%s)", cli, args, extra={"event.action": "invoke", "logrite.cli": cli})
        return super().invoke(cli, args, **kwargs)
