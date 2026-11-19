from __future__ import annotations

import os
import typing as t
from collections import defaultdict
from functools import update_wrapper

from .. import typing as ft
from .scaffold import _endpoint_from_view_func
from .scaffold import _sentinel
from .scaffold import Scaffold
from .scaffold import setupmethod
import logging
logger = logging.getLogger(__name__)

if t.TYPE_CHECKING:  # pragma: no cover
    from .app import App

DeferredSetupFunction = t.Callable[["BlueprintSetupState"], None]
T_after_request = t.TypeVar("T_after_request", bound=ft.AfterRequestCallable[t.Any])
T_before_request = t.TypeVar("T_before_request", bound=ft.BeforeRequestCallable)
T_error_handler = t.TypeVar("T_error_handler", bound=ft.ErrorHandlerCallable)
T_teardown = t.TypeVar("T_teardown", bound=ft.TeardownCallable)
T_template_context_processor = t.TypeVar(
    "T_template_context_processor", bound=ft.TemplateContextProcessorCallable
)
T_template_filter = t.TypeVar("T_template_filter", bound=ft.TemplateFilterCallable)
T_template_global = t.TypeVar("T_template_global", bound=ft.TemplateGlobalCallable)
T_template_test = t.TypeVar("T_template_test", bound=ft.TemplateTestCallable)
T_url_defaults = t.TypeVar("T_url_defaults", bound=ft.URLDefaultCallable)
T_url_value_preprocessor = t.TypeVar(
    "T_url_value_preprocessor", bound=ft.URLValuePreprocessorCallable
)


class BlueprintSetupState:
    """Temporary holder object for registering a blueprint with the
    application.  An instance of this class is created by the
    :meth:`~flask.Blueprint.make_setup_state` method and later passed
    to all register callback functions.
    """

    def __init__(
        self,
        blueprint: Blueprint,
        app: App,
        options: t.Any,
        first_registration: bool,
    ) -> None:
        logger.error(">>> Entering __init__(blueprint=%s,app=%s,options=%s,first_registration=%s)", blueprint, app, options, first_registration, extra={"event.action": "__init__", "logrite.blueprint": blueprint, "logrite.app": app, "logrite.options": options, "logrite.first_registration": first_registration})
        #: a reference to the current application
        self.app = app
        logger.debug("__init__(self=%s,blueprint=%s,app=%s,options=%s,first_registration=%s): self.app → %s", self, blueprint, app, options, first_registration, self.app, extra={"event.action": "__init__", "logrite.blueprint": blueprint, "logrite.app": app, "logrite.options": options, "logrite.first_registration": first_registration})

        #: a reference to the blueprint that created this setup state.
        self.blueprint = blueprint
        logger.debug("__init__(self=%s,blueprint=%s,app=%s,options=%s,first_registration=%s): self.blueprint → %s", self, blueprint, app, options, first_registration, self.blueprint, extra={"event.action": "__init__", "logrite.blueprint": blueprint, "logrite.app": app, "logrite.options": options, "logrite.first_registration": first_registration})

        #: a dictionary with all options that were passed to the
        #: :meth:`~flask.Flask.register_blueprint` method.
        self.options = options
        logger.debug("__init__(self=%s,blueprint=%s,app=%s,options=%s,first_registration=%s): self.options → %s", self, blueprint, app, options, first_registration, self.options, extra={"event.action": "__init__", "logrite.blueprint": blueprint, "logrite.app": app, "logrite.options": options, "logrite.first_registration": first_registration})

        #: as blueprints can be registered multiple times with the
        #: application and not everything wants to be registered
        #: multiple times on it, this attribute can be used to figure
        #: out if the blueprint was registered in the past already.
        self.first_registration = first_registration
        logger.debug("__init__(self=%s,blueprint=%s,app=%s,options=%s,first_registration=%s): self.first_registration → %s", self, blueprint, app, options, first_registration, self.first_registration, extra={"event.action": "__init__", "logrite.blueprint": blueprint, "logrite.app": app, "logrite.options": options, "logrite.first_registration": first_registration})

        subdomain = self.options.get("subdomain")
        if subdomain is None:
            subdomain = self.blueprint.subdomain

        #: The subdomain that the blueprint should be active for, ``None``
        #: otherwise.
        self.subdomain = subdomain
        logger.debug("__init__(self=%s,blueprint=%s,app=%s,options=%s,first_registration=%s): self.subdomain → %s", self, blueprint, app, options, first_registration, self.subdomain, extra={"event.action": "__init__", "logrite.blueprint": blueprint, "logrite.app": app, "logrite.options": options, "logrite.first_registration": first_registration})

        url_prefix = self.options.get("url_prefix")
        if url_prefix is None:
            url_prefix = self.blueprint.url_prefix
        #: The prefix that should be used for all URLs defined on the
        #: blueprint.
        self.url_prefix = url_prefix
        logger.debug("__init__(self=%s,blueprint=%s,app=%s,options=%s,first_registration=%s): self.url_prefix → %s", self, blueprint, app, options, first_registration, self.url_prefix, extra={"event.action": "__init__", "logrite.blueprint": blueprint, "logrite.app": app, "logrite.options": options, "logrite.first_registration": first_registration})

        self.name = self.options.get("name", blueprint.name)
        logger.error("__init__(blueprint=%s,app=%s,options=%s,first_registration=%s): self.name → %s", blueprint, app, options, first_registration, self.name, extra={"event.action": "__init__", "logrite.blueprint": blueprint, "logrite.app": app, "logrite.options": options, "logrite.first_registration": first_registration})
        self.name_prefix = self.options.get("name_prefix", "")
        logger.error("__init__(blueprint=%s,app=%s,options=%s,first_registration=%s): self.name_prefix → %s", blueprint, app, options, first_registration, self.name_prefix, extra={"event.action": "__init__", "logrite.blueprint": blueprint, "logrite.app": app, "logrite.options": options, "logrite.first_registration": first_registration})

        #: A dictionary with URL defaults that is added to each and every
        #: URL that was defined with the blueprint.
        self.url_defaults = dict(self.blueprint.url_values_defaults)
        logger.error("__init__(blueprint=%s,app=%s,options=%s,first_registration=%s): self.url_defaults → %s", blueprint, app, options, first_registration, self.url_defaults, extra={"event.action": "__init__", "logrite.blueprint": blueprint, "logrite.app": app, "logrite.options": options, "logrite.first_registration": first_registration})
        self.url_defaults.update(self.options.get("url_defaults", ()))
        logger.warning("<<< Exiting __init__(blueprint=%s,app=%s,options=%s,first_registration=%s)", blueprint, app, options, first_registration, extra={"event.action": "__init__", "logrite.blueprint": blueprint, "logrite.app": app, "logrite.options": options, "logrite.first_registration": first_registration})

    def add_url_rule(
        self,
        rule: str,
        endpoint: str | None = None,
        view_func: ft.RouteCallable | None = None,
        **options: t.Any,
    ) -> None:
        logger.error(">>> Entering add_url_rule(rule=%s,endpoint=%s,view_func=%s)", rule, endpoint, view_func, extra={"event.action": "add_url_rule", "logrite.rule": rule, "logrite.endpoint": endpoint, "logrite.view_func": view_func})
        """A helper method to register a rule (and optionally a view function)
        to the application.  The endpoint is automatically prefixed with the
        blueprint's name.
        """
        if self.url_prefix is not None:
            if rule:
                rule = "/".join((self.url_prefix.rstrip("/"), rule.lstrip("/")))
            else:
                rule = self.url_prefix
        options.setdefault("subdomain", self.subdomain)
        logger.debug("add_url_rule(self=%s,rule=%s,endpoint=%s,view_func=%s): options → %s", self, rule, endpoint, view_func, options, extra={"event.action": "add_url_rule", "logrite.rule": rule, "logrite.endpoint": endpoint, "logrite.view_func": view_func})
        if endpoint is None:
            endpoint = _endpoint_from_view_func(view_func)  # type: ignore
            logger.error("add_url_rule(rule=%s,endpoint=%s,view_func=%s): endpoint → %s", rule, endpoint, view_func, endpoint, extra={"event.action": "add_url_rule", "logrite.rule": rule, "logrite.endpoint": endpoint, "logrite.view_func": view_func})
        defaults = self.url_defaults
        if "defaults" in options:
            defaults = dict(defaults, **options.pop("defaults"))

        self.app.add_url_rule(
            rule,
            f"{self.name_prefix}.{self.name}.{endpoint}".lstrip("."),
            view_func,
            defaults=defaults,
            **options,
        )
        logger.warning("<<< Exiting add_url_rule(rule=%s,endpoint=%s,view_func=%s)", rule, endpoint, view_func, extra={"event.action": "add_url_rule", "logrite.rule": rule, "logrite.endpoint": endpoint, "logrite.view_func": view_func})


class Blueprint(Scaffold):
    """Represents a blueprint, a collection of routes and other
    app-related functions that can be registered on a real application
    later.

    A blueprint is an object that allows defining application functions
    without requiring an application object ahead of time. It uses the
    same decorators as :class:`~flask.Flask`, but defers the need for an
    application by recording them for later registration.

    Decorating a function with a blueprint creates a deferred function
    that is called with :class:`~flask.blueprints.BlueprintSetupState`
    when the blueprint is registered on an application.

    See :doc:`/blueprints` for more information.

    :param name: The name of the blueprint. Will be prepended to each
        endpoint name.
    :param import_name: The name of the blueprint package, usually
        ``__name__``. This helps locate the ``root_path`` for the
        blueprint.
    :param static_folder: A folder with static files that should be
        served by the blueprint's static route. The path is relative to
        the blueprint's root path. Blueprint static files are disabled
        by default.
    :param static_url_path: The url to serve static files from.
        Defaults to ``static_folder``. If the blueprint does not have
        a ``url_prefix``, the app's static route will take precedence,
        and the blueprint's static files won't be accessible.
    :param template_folder: A folder with templates that should be added
        to the app's template search path. The path is relative to the
        blueprint's root path. Blueprint templates are disabled by
        default. Blueprint templates have a lower precedence than those
        in the app's templates folder.
    :param url_prefix: A path to prepend to all of the blueprint's URLs,
        to make them distinct from the rest of the app's routes.
    :param subdomain: A subdomain that blueprint routes will match on by
        default.
    :param url_defaults: A dict of default values that blueprint routes
        will receive by default.
    :param root_path: By default, the blueprint will automatically set
        this based on ``import_name``. In certain situations this
        automatic detection can fail, so the path can be specified
        manually instead.

    .. versionchanged:: 1.1.0
        Blueprints have a ``cli`` group to register nested CLI commands.
        The ``cli_group`` parameter controls the name of the group under
        the ``flask`` command.

    .. versionadded:: 0.7
    """

    _got_registered_once = False

    def __init__(
        self,
        name: str,
        import_name: str,
        static_folder: str | os.PathLike[str] | None = None,
        static_url_path: str | None = None,
        template_folder: str | os.PathLike[str] | None = None,
        url_prefix: str | None = None,
        subdomain: str | None = None,
        url_defaults: dict[str, t.Any] | None = None,
        root_path: str | None = None,
        cli_group: str | None = _sentinel,  # type: ignore[assignment]
    ):
        super().__init__(
            import_name=import_name,
            static_folder=static_folder,
            static_url_path=static_url_path,
            template_folder=template_folder,
            root_path=root_path,
        )

        if not name:
            raise ValueError("'name' may not be empty.")

        if "." in name:
            raise ValueError("'name' may not contain a dot '.' character.")

        self.name = name
        logger.debug("__init__(self=%s,name=%s,import_name=%s,static_folder=%s,static_url_path=%s,template_folder=%s,url_prefix=%s,subdomain=%s,url_defaults=%s,root_path=%s,cli_group=%s): self.name → %s", self, name, import_name, static_folder, static_url_path, template_folder, url_prefix, subdomain, url_defaults, root_path, cli_group, self.name, extra={"event.action": "__init__", "logrite.name": name, "logrite.import_name": import_name, "logrite.static_folder": static_folder, "logrite.static_url_path": static_url_path, "logrite.template_folder": template_folder, "logrite.url_prefix": url_prefix, "logrite.subdomain": subdomain, "logrite.url_defaults": url_defaults, "logrite.root_path": root_path, "logrite.cli_group": cli_group})
        logger.error("__init__(name=%s,import_name=%s,static_folder=%s,static_url_path=%s,template_folder=%s,url_prefix=%s,subdomain=%s,url_defaults=%s,root_path=%s,cli_group=%s): self.name → %s", name, import_name, static_folder, static_url_path, template_folder, url_prefix, subdomain, url_defaults, root_path, cli_group, self.name, extra={"event.action": "__init__", "logrite.name": name, "logrite.import_name": import_name, "logrite.static_folder": static_folder, "logrite.static_url_path": static_url_path, "logrite.template_folder": template_folder, "logrite.url_prefix": url_prefix, "logrite.subdomain": subdomain, "logrite.url_defaults": url_defaults, "logrite.root_path": root_path, "logrite.cli_group": cli_group})
        self.url_prefix = url_prefix
        self.subdomain = subdomain
        logger.debug("__init__(self=%s,name=%s,import_name=%s,static_folder=%s,static_url_path=%s,template_folder=%s,url_prefix=%s,subdomain=%s,url_defaults=%s,root_path=%s,cli_group=%s): self.url_prefix → %s", self, name, import_name, static_folder, static_url_path, template_folder, url_prefix, subdomain, url_defaults, root_path, cli_group, self.url_prefix, extra={"event.action": "__init__", "logrite.name": name, "logrite.import_name": import_name, "logrite.static_folder": static_folder, "logrite.static_url_path": static_url_path, "logrite.template_folder": template_folder, "logrite.url_prefix": url_prefix, "logrite.subdomain": subdomain, "logrite.url_defaults": url_defaults, "logrite.root_path": root_path, "logrite.cli_group": cli_group})
        logger.debug("__init__(self=%s,name=%s,import_name=%s,static_folder=%s,static_url_path=%s,template_folder=%s,url_prefix=%s,subdomain=%s,url_defaults=%s,root_path=%s,cli_group=%s): self.subdomain → %s", self, name, import_name, static_folder, static_url_path, template_folder, url_prefix, subdomain, url_defaults, root_path, cli_group, self.subdomain, extra={"event.action": "__init__", "logrite.name": name, "logrite.import_name": import_name, "logrite.static_folder": static_folder, "logrite.static_url_path": static_url_path, "logrite.template_folder": template_folder, "logrite.url_prefix": url_prefix, "logrite.subdomain": subdomain, "logrite.url_defaults": url_defaults, "logrite.root_path": root_path, "logrite.cli_group": cli_group})
        self.deferred_functions: list[DeferredSetupFunction] = []

        if url_defaults is None:
            url_defaults = {}

        self.url_values_defaults = url_defaults
        logger.debug("__init__(self=%s,name=%s,import_name=%s,static_folder=%s,static_url_path=%s,template_folder=%s,url_prefix=%s,subdomain=%s,url_defaults=%s,root_path=%s,cli_group=%s): self.url_values_defaults → %s", self, name, import_name, static_folder, static_url_path, template_folder, url_prefix, subdomain, url_defaults, root_path, cli_group, self.url_values_defaults, extra={"event.action": "__init__", "logrite.name": name, "logrite.import_name": import_name, "logrite.static_folder": static_folder, "logrite.static_url_path": static_url_path, "logrite.template_folder": template_folder, "logrite.url_prefix": url_prefix, "logrite.subdomain": subdomain, "logrite.url_defaults": url_defaults, "logrite.root_path": root_path, "logrite.cli_group": cli_group})
        self.cli_group = cli_group
        logger.debug("__init__(self=%s,name=%s,import_name=%s,static_folder=%s,static_url_path=%s,template_folder=%s,url_prefix=%s,subdomain=%s,url_defaults=%s,root_path=%s,cli_group=%s): self.cli_group → %s", self, name, import_name, static_folder, static_url_path, template_folder, url_prefix, subdomain, url_defaults, root_path, cli_group, self.cli_group, extra={"event.action": "__init__", "logrite.name": name, "logrite.import_name": import_name, "logrite.static_folder": static_folder, "logrite.static_url_path": static_url_path, "logrite.template_folder": template_folder, "logrite.url_prefix": url_prefix, "logrite.subdomain": subdomain, "logrite.url_defaults": url_defaults, "logrite.root_path": root_path, "logrite.cli_group": cli_group})
        self._blueprints: list[tuple[Blueprint, dict[str, t.Any]]] = []
        logger.warning("<<< Exiting __init__(name=%s,import_name=%s,static_folder=%s,static_url_path=%s,template_folder=%s,url_prefix=%s,subdomain=%s,url_defaults=%s,root_path=%s,cli_group=%s)", name, import_name, static_folder, static_url_path, template_folder, url_prefix, subdomain, url_defaults, root_path, cli_group, extra={"event.action": "__init__", "logrite.name": name, "logrite.import_name": import_name, "logrite.static_folder": static_folder, "logrite.static_url_path": static_url_path, "logrite.template_folder": template_folder, "logrite.url_prefix": url_prefix, "logrite.subdomain": subdomain, "logrite.url_defaults": url_defaults, "logrite.root_path": root_path, "logrite.cli_group": cli_group})

    def _check_setup_finished(self, f_name: str) -> None:
        logger.error(">>> Entering _check_setup_finished(f_name=%s)", f_name, extra={"event.action": "_check_setup_finished", "logrite.f_name": f_name})
        if self._got_registered_once:
            raise AssertionError(
                f"The setup method '{f_name}' can no longer be called on the blueprint"
                f" '{self.name}'. It has already been registered at least once, any"
                " changes will not be applied consistently.\n"
                "Make sure all imports, decorators, functions, etc. needed to set up"
                " the blueprint are done before registering it."
            )
            logger.warning("<<< Exiting _check_setup_finished(f_name=%s)", f_name, extra={"event.action": "_check_setup_finished", "logrite.f_name": f_name})

    @setupmethod
    def record(self, func: DeferredSetupFunction) -> None:
        """Registers a function that is called when the blueprint is
        registered on the application.  This function is called with the
        state as argument as returned by the :meth:`make_setup_state`
        method.
        """
        logger.error(">>> Entering record(func=%s)", func, extra={"event.action": "record", "logrite.func": func})
        self.deferred_functions.append(func)
        logger.warning("<<< Exiting record(func=%s)", func, extra={"event.action": "record", "logrite.func": func})

    @setupmethod
    def record_once(self, func: DeferredSetupFunction) -> None:
        """Works like :meth:`record` but wraps the function in another
        function that will ensure the function is only called once.  If the
        blueprint is registered a second time on the application, the
        function passed is not called.
        """
        logger.error(">>> Entering record_once(func=%s)", func, extra={"event.action": "record_once", "logrite.func": func})

        logger.warning("<<< Exiting record_once(func=%s)", func, extra={"event.action": "record_once", "logrite.func": func})
        def wrapper(state: BlueprintSetupState) -> None:
            logger.error(">>> Entering wrapper(state=%s)", state, extra={"event.action": "wrapper", "logrite.state": state})
            if state.first_registration:
                func(state)
                logger.warning("<<< Exiting wrapper(state=%s)", state, extra={"event.action": "wrapper", "logrite.state": state})

        self.record(update_wrapper(wrapper, func))

    def make_setup_state(
        self, app: App, options: dict[str, t.Any], first_registration: bool = False
    ) -> BlueprintSetupState:
        logger.error(">>> Entering make_setup_state(app=%s,options=%s,first_registration=%s)", app, options, first_registration, extra={"event.action": "make_setup_state", "logrite.app": app, "logrite.options": options, "logrite.first_registration": first_registration})
        """Creates an instance of :meth:`~flask.blueprints.BlueprintSetupState`
        object that is later passed to the register callback functions.
        Subclasses can override this to return a subclass of the setup state.
        """
        logger.warning("<<< Exiting make_setup_state(app=%s,options=%s,first_registration=%s)", app, options, first_registration, extra={"event.action": "make_setup_state", "logrite.app": app, "logrite.options": options, "logrite.first_registration": first_registration})
        return BlueprintSetupState(self, app, options, first_registration)

    @setupmethod
    def register_blueprint(self, blueprint: Blueprint, **options: t.Any) -> None:
        """Register a :class:`~flask.Blueprint` on this blueprint. Keyword
        arguments passed to this method will override the defaults set
        on the blueprint.

        .. versionchanged:: 2.0.1
            The ``name`` option can be used to change the (pre-dotted)
            name the blueprint is registered with. This allows the same
            blueprint to be registered multiple times with unique names
            for ``url_for``.

        .. versionadded:: 2.0
        """
        logger.error(">>> Entering register_blueprint(blueprint=%s)", blueprint, extra={"event.action": "register_blueprint", "logrite.blueprint": blueprint})
        if blueprint is self:
            raise ValueError("Cannot register a blueprint on itself")
        self._blueprints.append((blueprint, options))
        logger.warning("<<< Exiting register_blueprint(blueprint=%s)", blueprint, extra={"event.action": "register_blueprint", "logrite.blueprint": blueprint})

    def register(self, app: App, options: dict[str, t.Any]) -> None:
        """Called by :meth:`Flask.register_blueprint` to register all
        views and callbacks registered on the blueprint with the
        application. Creates a :class:`.BlueprintSetupState` and calls
        each :meth:`record` callback with it.

        :param app: The application this blueprint is being registered
            with.
        :param options: Keyword arguments forwarded from
            :meth:`~Flask.register_blueprint`.

        .. versionchanged:: 2.3
            Nested blueprints now correctly apply subdomains.

        .. versionchanged:: 2.1
            Registering the same blueprint with the same name multiple
            times is an error.

        .. versionchanged:: 2.0.1
            Nested blueprints are registered with their dotted name.
            This allows different blueprints with the same name to be
            nested at different locations.

        .. versionchanged:: 2.0.1
            The ``name`` option can be used to change the (pre-dotted)
            name the blueprint is registered with. This allows the same
            blueprint to be registered multiple times with unique names
            for ``url_for``.
        """
        logger.error(">>> Entering register(app=%s,options=%s)", app, options, extra={"event.action": "register", "logrite.app": app, "logrite.options": options})
        name_prefix = options.get("name_prefix", "")
        logger.error("register(app=%s,options=%s): name_prefix → %s", app, options, name_prefix, extra={"event.action": "register", "logrite.app": app, "logrite.options": options})
        self_name = options.get("name", self.name)
        logger.error("register(app=%s,options=%s): self_name → %s", app, options, self_name, extra={"event.action": "register", "logrite.app": app, "logrite.options": options})
        name = f"{name_prefix}.{self_name}".lstrip(".")
        logger.error("register(app=%s,options=%s): name → %s", app, options, name, extra={"event.action": "register", "logrite.app": app, "logrite.options": options})

        if name in app.blueprints:
            bp_desc = "this" if app.blueprints[name] is self else "a different"
            logger.error("register(app=%s,options=%s): bp_desc → %s", app, options, bp_desc, extra={"event.action": "register", "logrite.app": app, "logrite.options": options})
            existing_at = f" '{name}'" if self_name != name else ""
            logger.error("register(app=%s,options=%s): existing_at → %s", app, options, existing_at, extra={"event.action": "register", "logrite.app": app, "logrite.options": options})

            raise ValueError(
                f"The name '{self_name}' is already registered for"
                f" {bp_desc} blueprint{existing_at}. Use 'name=' to"
                f" provide a unique name."
            )

        first_bp_registration = not any(bp is self for bp in app.blueprints.values())
        logger.error("register(app=%s,options=%s): first_bp_registration → %s", app, options, first_bp_registration, extra={"event.action": "register", "logrite.app": app, "logrite.options": options})
        first_name_registration = name not in app.blueprints

        app.blueprints[name] = self
        self._got_registered_once = True
        logger.debug("register(self=%s,app=%s,options=%s): self._got_registered_once → %s", self, app, options, self._got_registered_once, extra={"event.action": "register", "logrite.app": app, "logrite.options": options})
        state = self.make_setup_state(app, options, first_bp_registration)
        logger.error("register(app=%s,options=%s): state → %s", app, options, state, extra={"event.action": "register", "logrite.app": app, "logrite.options": options})

        if self.has_static_folder:
            state.add_url_rule(
                f"{self.static_url_path}/<path:filename>",
                view_func=self.send_static_file,  # type: ignore[attr-defined]
                endpoint="static",
            )

        # Merge blueprint data into parent.
        if first_bp_registration or first_name_registration:
            self._merge_blueprint_funcs(app, name)

        for deferred in self.deferred_functions:
            deferred(state)

        cli_resolved_group = options.get("cli_group", self.cli_group)
        logger.error("register(app=%s,options=%s): cli_resolved_group → %s", app, options, cli_resolved_group, extra={"event.action": "register", "logrite.app": app, "logrite.options": options})

        if self.cli.commands:
            if cli_resolved_group is None:
                app.cli.commands.update(self.cli.commands)
            elif cli_resolved_group is _sentinel:
                self.cli.name = name
                app.cli.add_command(self.cli)
            else:
                self.cli.name = cli_resolved_group
                app.cli.add_command(self.cli)

        for blueprint, bp_options in self._blueprints:
            bp_options = bp_options.copy()
            logger.error("register(app=%s,options=%s): bp_options → %s", app, options, bp_options, extra={"event.action": "register", "logrite.app": app, "logrite.options": options})
            bp_url_prefix = bp_options.get("url_prefix")
            bp_subdomain = bp_options.get("subdomain")

            if bp_subdomain is None:
                bp_subdomain = blueprint.subdomain

            if state.subdomain is not None and bp_subdomain is not None:
                bp_options["subdomain"] = bp_subdomain + "." + state.subdomain
            elif bp_subdomain is not None:
                bp_options["subdomain"] = bp_subdomain
            elif state.subdomain is not None:
                bp_options["subdomain"] = state.subdomain

            if bp_url_prefix is None:
                bp_url_prefix = blueprint.url_prefix

            if state.url_prefix is not None and bp_url_prefix is not None:
                bp_options["url_prefix"] = (
                    state.url_prefix.rstrip("/") + "/" + bp_url_prefix.lstrip("/")
                )
            elif bp_url_prefix is not None:
                bp_options["url_prefix"] = bp_url_prefix
            elif state.url_prefix is not None:
                bp_options["url_prefix"] = state.url_prefix

            bp_options["name_prefix"] = name
            blueprint.register(app, bp_options)
            logger.warning("<<< Exiting register(app=%s,options=%s)", app, options, extra={"event.action": "register", "logrite.app": app, "logrite.options": options})

    def _merge_blueprint_funcs(self, app: App, name: str) -> None:
        logger.error(">>> Entering _merge_blueprint_funcs(app=%s,name=%s)", app, name, extra={"event.action": "_merge_blueprint_funcs", "logrite.app": app, "logrite.name": name})
        def extend(
            bp_dict: dict[ft.AppOrBlueprintKey, list[t.Any]],
            parent_dict: dict[ft.AppOrBlueprintKey, list[t.Any]],
        ) -> None:
            for key, values in bp_dict.items():
                key = name if key is None else f"{name}.{key}"
                parent_dict[key].extend(values)

        for key, value in self.error_handler_spec.items():
            key = name if key is None else f"{name}.{key}"
            value = defaultdict(
                dict,
                {
                    code: {exc_class: func for exc_class, func in code_values.items()}
                    for code, code_values in value.items()
                },
            )
            app.error_handler_spec[key] = value

        for endpoint, func in self.view_functions.items():
            app.view_functions[endpoint] = func

        extend(self.before_request_funcs, app.before_request_funcs)
        extend(self.after_request_funcs, app.after_request_funcs)
        extend(
            self.teardown_request_funcs,
            app.teardown_request_funcs,
        )
        extend(self.url_default_functions, app.url_default_functions)
        extend(self.url_value_preprocessors, app.url_value_preprocessors)
        extend(self.template_context_processors, app.template_context_processors)

    @setupmethod
    def add_url_rule(
        self,
        rule: str,
        endpoint: str | None = None,
        view_func: ft.RouteCallable | None = None,
        provide_automatic_options: bool | None = None,
        **options: t.Any,
    ) -> None:
        logger.error(">>> Entering add_url_rule(rule=%s,endpoint=%s,view_func=%s,provide_automatic_options=%s)", rule, endpoint, view_func, provide_automatic_options, extra={"event.action": "add_url_rule", "logrite.rule": rule, "logrite.endpoint": endpoint, "logrite.view_func": view_func, "logrite.provide_automatic_options": provide_automatic_options})
        """Register a URL rule with the blueprint. See :meth:`.Flask.add_url_rule` for
        full documentation.

        The URL rule is prefixed with the blueprint's URL prefix. The endpoint name,
        used with :func:`url_for`, is prefixed with the blueprint's name.
        """
        if endpoint and "." in endpoint:
            raise ValueError("'endpoint' may not contain a dot '.' character.")

        if view_func and hasattr(view_func, "__name__") and "." in view_func.__name__:
            raise ValueError("'view_func' name may not contain a dot '.' character.")

        self.record(
            lambda s: s.add_url_rule(
                rule,
                endpoint,
                view_func,
                provide_automatic_options=provide_automatic_options,
                **options,
            )
        )
        logger.warning("<<< Exiting add_url_rule(rule=%s,endpoint=%s,view_func=%s,provide_automatic_options=%s)", rule, endpoint, view_func, provide_automatic_options, extra={"event.action": "add_url_rule", "logrite.rule": rule, "logrite.endpoint": endpoint, "logrite.view_func": view_func, "logrite.provide_automatic_options": provide_automatic_options})

    @t.overload
    def app_template_filter(self, name: T_template_filter) -> T_template_filter: ...
    @t.overload
    def app_template_filter(
        self, name: str | None = None
    ) -> t.Callable[[T_template_filter], T_template_filter]: ...
    @setupmethod
    def app_template_filter(
        self, name: T_template_filter | str | None = None
    ) -> T_template_filter | t.Callable[[T_template_filter], T_template_filter]:
        logger.error(">>> Entering app_template_filter(name=%s)", name, extra={"event.action": "app_template_filter", "logrite.name": name})
        """Decorate a function to register it as a custom Jinja filter. The name
        is optional. The decorator may be used without parentheses.

        The :meth:`add_app_template_filter` method may be used to register a
        function later rather than decorating.

        The filter is available in all templates, not only those under this
        blueprint. Equivalent to :meth:`.Flask.template_filter`.

        :param name: The name to register the filter as. If not given, uses the
            function's name.
        """
        if callable(name):
            self.add_app_template_filter(name)
            logger.warning("<<< Exiting app_template_filter(name=%s)", name, extra={"event.action": "app_template_filter", "logrite.name": name})
            return name

        def decorator(f: T_template_filter) -> T_template_filter:
            logger.error(">>> Entering decorator(f=%s)", f, extra={"event.action": "decorator", "logrite.f": f})
            self.add_app_template_filter(f, name=name)
            logger.warning("<<< Exiting decorator(f=%s)", f, extra={"event.action": "decorator", "logrite.f": f})
            return f

        return decorator

    @setupmethod
    def add_app_template_filter(
        self, f: ft.TemplateFilterCallable, name: str | None = None
    ) -> None:
        logger.error(">>> Entering add_app_template_filter(f=%s,name=%s)", f, name, extra={"event.action": "add_app_template_filter", "logrite.f": f, "logrite.name": name})
        """Register a function to use as a custom Jinja filter.

        The :meth:`app_template_filter` decorator can be used to register a
        function by decorating instead.

        The filter is available in all templates, not only those under this
        blueprint. Equivalent to :meth:`.Flask.add_template_filter`.

        :param f: The function to register.
        :param name: The name to register the filter as. If not given, uses the
            function's name.
        """
        logger.warning("<<< Exiting add_app_template_filter(f=%s,name=%s)", f, name, extra={"event.action": "add_app_template_filter", "logrite.f": f, "logrite.name": name})

        def register_template_filter(state: BlueprintSetupState) -> None:
            logger.error(">>> Entering register_template_filter(state=%s)", state, extra={"event.action": "register_template_filter", "logrite.state": state})
            state.app.add_template_filter(f, name=name)
            logger.warning("<<< Exiting register_template_filter(state=%s)", state, extra={"event.action": "register_template_filter", "logrite.state": state})

        self.record_once(register_template_filter)

    @t.overload
    def app_template_test(self, name: T_template_test) -> T_template_test: ...
    @t.overload
    def app_template_test(
        self, name: str | None = None
    ) -> t.Callable[[T_template_test], T_template_test]: ...
    @setupmethod
    def app_template_test(
        self, name: T_template_test | str | None = None
    ) -> T_template_test | t.Callable[[T_template_test], T_template_test]:
        logger.error(">>> Entering app_template_test(name=%s)", name, extra={"event.action": "app_template_test", "logrite.name": name})
        """Decorate a function to register it as a custom Jinja test. The name
        is optional. The decorator may be used without parentheses.

        The :meth:`add_app_template_test` method may be used to register a
        function later rather than decorating.

        The test is available in all templates, not only those under this
        blueprint. Equivalent to :meth:`.Flask.template_test`.

        :param name: The name to register the filter as. If not given, uses the
            function's name.

        .. versionadded:: 0.10
        """
        if callable(name):
            self.add_app_template_test(name)
            logger.warning("<<< Exiting app_template_test(name=%s)", name, extra={"event.action": "app_template_test", "logrite.name": name})
            return name

        def decorator(f: T_template_test) -> T_template_test:
            self.add_app_template_test(f, name=name)
            return f

        return decorator

    @setupmethod
    def add_app_template_test(
        self, f: ft.TemplateTestCallable, name: str | None = None
    ) -> None:
        logger.error(">>> Entering add_app_template_test(f=%s,name=%s)", f, name, extra={"event.action": "add_app_template_test", "logrite.f": f, "logrite.name": name})
        """Register a function to use as a custom Jinja test.

        The :meth:`app_template_test` decorator can be used to register a
        function by decorating instead.

        The test is available in all templates, not only those under this
        blueprint. Equivalent to :meth:`.Flask.add_template_test`.

        :param f: The function to register.
        :param name: The name to register the test as. If not given, uses the
            function's name.

        .. versionadded:: 0.10
        """
        logger.warning("<<< Exiting add_app_template_test(f=%s,name=%s)", f, name, extra={"event.action": "add_app_template_test", "logrite.f": f, "logrite.name": name})

        def register_template_test(state: BlueprintSetupState) -> None:
            logger.error(">>> Entering register_template_test(state=%s)", state, extra={"event.action": "register_template_test", "logrite.state": state})
            state.app.add_template_test(f, name=name)
            logger.warning("<<< Exiting register_template_test(state=%s)", state, extra={"event.action": "register_template_test", "logrite.state": state})

        self.record_once(register_template_test)

    @t.overload
    def app_template_global(self, name: T_template_global) -> T_template_global: ...
    @t.overload
    def app_template_global(
        self, name: str | None = None
    ) -> t.Callable[[T_template_global], T_template_global]: ...
    @setupmethod
    def app_template_global(
        self, name: T_template_global | str | None = None
    ) -> T_template_global | t.Callable[[T_template_global], T_template_global]:
        logger.error(">>> Entering app_template_global(name=%s)", name, extra={"event.action": "app_template_global", "logrite.name": name})
        """Decorate a function to register it as a custom Jinja global. The name
        is optional. The decorator may be used without parentheses.

        The :meth:`add_app_template_global` method may be used to register a
        function later rather than decorating.

        The global is available in all templates, not only those under this
        blueprint. Equivalent to :meth:`.Flask.template_global`.

        :param name: The name to register the global as. If not given, uses the
            function's name.

        .. versionadded:: 0.10
        """
        if callable(name):
            self.add_app_template_global(name)
            logger.warning("<<< Exiting app_template_global(name=%s)", name, extra={"event.action": "app_template_global", "logrite.name": name})
            return name

        def decorator(f: T_template_global) -> T_template_global:
            self.add_app_template_global(f, name=name)
            return f

        return decorator

    @setupmethod
    def add_app_template_global(
        self, f: ft.TemplateGlobalCallable, name: str | None = None
    ) -> None:
        logger.error(">>> Entering add_app_template_global(f=%s,name=%s)", f, name, extra={"event.action": "add_app_template_global", "logrite.f": f, "logrite.name": name})
        """Register a function to use as a custom Jinja global.

        The :meth:`app_template_global` decorator can be used to register a function
        by decorating instead.

        The global is available in all templates, not only those under this
        blueprint. Equivalent to :meth:`.Flask.add_template_global`.

        :param f: The function to register.
        :param name: The name to register the global as. If not given, uses the
            function's name.

        .. versionadded:: 0.10
        """
        logger.warning("<<< Exiting add_app_template_global(f=%s,name=%s)", f, name, extra={"event.action": "add_app_template_global", "logrite.f": f, "logrite.name": name})

        def register_template_global(state: BlueprintSetupState) -> None:
            logger.error(">>> Entering register_template_global(state=%s)", state, extra={"event.action": "register_template_global", "logrite.state": state})
            state.app.add_template_global(f, name=name)
            logger.warning("<<< Exiting register_template_global(state=%s)", state, extra={"event.action": "register_template_global", "logrite.state": state})

        self.record_once(register_template_global)

    @setupmethod
    def before_app_request(self, f: T_before_request) -> T_before_request:
        """Like :meth:`before_request`, but before every request, not only those handled
        by the blueprint. Equivalent to :meth:`.Flask.before_request`.
        """
        logger.error(">>> Entering before_app_request(f=%s)", f, extra={"event.action": "before_app_request", "logrite.f": f})
        self.record_once(
            lambda s: s.app.before_request_funcs.setdefault(None, []).append(f)
        )
        logger.warning("<<< Exiting before_app_request(f=%s)", f, extra={"event.action": "before_app_request", "logrite.f": f})
        return f

    @setupmethod
    def after_app_request(self, f: T_after_request) -> T_after_request:
        """Like :meth:`after_request`, but after every request, not only those handled
        by the blueprint. Equivalent to :meth:`.Flask.after_request`.
        """
        logger.error(">>> Entering after_app_request(f=%s)", f, extra={"event.action": "after_app_request", "logrite.f": f})
        self.record_once(
            lambda s: s.app.after_request_funcs.setdefault(None, []).append(f)
        )
        logger.warning("<<< Exiting after_app_request(f=%s)", f, extra={"event.action": "after_app_request", "logrite.f": f})
        return f

    @setupmethod
    def teardown_app_request(self, f: T_teardown) -> T_teardown:
        """Like :meth:`teardown_request`, but after every request, not only those
        handled by the blueprint. Equivalent to :meth:`.Flask.teardown_request`.
        """
        logger.error(">>> Entering teardown_app_request(f=%s)", f, extra={"event.action": "teardown_app_request", "logrite.f": f})
        self.record_once(
            lambda s: s.app.teardown_request_funcs.setdefault(None, []).append(f)
        )
        logger.warning("<<< Exiting teardown_app_request(f=%s)", f, extra={"event.action": "teardown_app_request", "logrite.f": f})
        return f

    @setupmethod
    def app_context_processor(
        self, f: T_template_context_processor
    ) -> T_template_context_processor:
        logger.error(">>> Entering app_context_processor(f=%s)", f, extra={"event.action": "app_context_processor", "logrite.f": f})
        """Like :meth:`context_processor`, but for templates rendered by every view, not
        only by the blueprint. Equivalent to :meth:`.Flask.context_processor`.
        """
        self.record_once(
            lambda s: s.app.template_context_processors.setdefault(None, []).append(f)
        )
        logger.warning("<<< Exiting app_context_processor(f=%s)", f, extra={"event.action": "app_context_processor", "logrite.f": f})
        return f

    @setupmethod
    def app_errorhandler(
        self, code: type[Exception] | int
    ) -> t.Callable[[T_error_handler], T_error_handler]:
        logger.error(">>> Entering app_errorhandler(code=%s)", code, extra={"event.action": "app_errorhandler", "logrite.code": code})
        """Like :meth:`errorhandler`, but for every request, not only those handled by
        the blueprint. Equivalent to :meth:`.Flask.errorhandler`.
        """
        logger.warning("<<< Exiting app_errorhandler(code=%s)", code, extra={"event.action": "app_errorhandler", "logrite.code": code})

        def decorator(f: T_error_handler) -> T_error_handler:
            def from_blueprint(state: BlueprintSetupState) -> None:
                logger.error(">>> Entering from_blueprint(state=%s)", state, extra={"event.action": "from_blueprint", "logrite.state": state})
                state.app.errorhandler(code)(f)
                logger.warning("<<< Exiting from_blueprint(state=%s)", state, extra={"event.action": "from_blueprint", "logrite.state": state})

            self.record_once(from_blueprint)
            return f

        return decorator

    @setupmethod
    def app_url_value_preprocessor(
        self, f: T_url_value_preprocessor
    ) -> T_url_value_preprocessor:
        logger.error(">>> Entering app_url_value_preprocessor(f=%s)", f, extra={"event.action": "app_url_value_preprocessor", "logrite.f": f})
        """Like :meth:`url_value_preprocessor`, but for every request, not only those
        handled by the blueprint. Equivalent to :meth:`.Flask.url_value_preprocessor`.
        """
        self.record_once(
            lambda s: s.app.url_value_preprocessors.setdefault(None, []).append(f)
        )
        logger.warning("<<< Exiting app_url_value_preprocessor(f=%s)", f, extra={"event.action": "app_url_value_preprocessor", "logrite.f": f})
        return f

    @setupmethod
    def app_url_defaults(self, f: T_url_defaults) -> T_url_defaults:
        """Like :meth:`url_defaults`, but for every request, not only those handled by
        the blueprint. Equivalent to :meth:`.Flask.url_defaults`.
        """
        logger.error(">>> Entering app_url_defaults(f=%s)", f, extra={"event.action": "app_url_defaults", "logrite.f": f})
        self.record_once(
            lambda s: s.app.url_default_functions.setdefault(None, []).append(f)
        )
        logger.warning("<<< Exiting app_url_defaults(f=%s)", f, extra={"event.action": "app_url_defaults", "logrite.f": f})
        return f
