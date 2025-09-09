# ruff: noqa: PLC0415

# Standard Library Imports
import json
import logging
from collections.abc import Iterable
from typing import Any

# Third Party Imports
from django.apps import AppConfig
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.translation import gettext_lazy as _
from health_check.plugins import plugin_dir

# Logger
logger: logging.Logger = logging.getLogger(__name__)


# Common App Configuration Class
class CommonConfig(AppConfig):
    """
    Common App Configuration Class.
    """

    # Attributes
    name: str = "apps.common"
    verbose_name: str = _("Common")

    # Ready Function
    def ready(self) -> None:
        """
        Register Health Check Backends And Apply Silk Patches.
        """
        # Apply Silk Patches
        self._patch_silk_json_handling()

        # Local Imports
        from apps.common.extensions.jwt_authentication_extension import JWTAuthenticationExtension  # noqa: F401
        from apps.common.health_checks.elasticsearch_health_check import ElasticsearchHealthCheck
        from apps.common.health_checks.jaeger_health_check import JaegerHealthCheck
        from apps.common.health_checks.mailpit_health_check import MailpitSMTPHealthCheck
        from apps.common.health_checks.prometheus_health_check import PrometheusHealthCheck
        from apps.common.health_checks.redis_health_check import RedisHealthCheck

        # Register The Health Check Backends
        plugin_dir.register(ElasticsearchHealthCheck)
        plugin_dir.register(MailpitSMTPHealthCheck)
        plugin_dir.register(JaegerHealthCheck)
        plugin_dir.register(PrometheusHealthCheck)
        plugin_dir.register(RedisHealthCheck)

    # Patch Silk JSON Handling
    def _patch_silk_json_handling(self) -> None:
        """
        Patch Silk JSON Handling To Prevent Jsonb Serialization Issues.
        """

        try:
            # Third Party Imports
            import silk.sql

            # Patch Force Str
            self._patch_force_str(silk.sql)

            # Patch Explain Query
            self._patch_explain_query(silk.sql)

        except ImportError:
            # Create Log Message
            log_message: str = "Silk Not Installed; Skipping JSON Handling Patch"

            # Log Exception
            logger.exception(log_message)

        except Exception:
            # Create Log Message
            log_message: str = "JSON Handling Patch Failed; Continuing Without Patch"

            # Log Exception
            logger.exception(log_message)

    # Patch Force Str
    def _patch_force_str(self, sql_module: Any) -> None:
        """
        Patch Silk's force_str Function To Handle JSONB Serialization.

        Args:
            sql_module (Any): Silk SQL Module To Patch.
        """

        # Force Str With Fallback
        def force_str_with_fallback(param: object) -> str:
            """
            Convert Parameter To String With JSON Safety.

            Args:
                param (object): Parameter To Convert.

            Returns:
                str: Converted String Representation.
            """
            # Serialize Parameter
            serialized = self._serialize_param(param)

            # If Serialized Is Not None
            if serialized is not None:
                # Return Serialized
                return serialized

            try:
                # Third Party Imports
                from silk.utils.encoding import force_str  # pyright: ignore[reportMissingImports]

                # Return Force Str
                return force_str(param)

            except ImportError:
                # Return String
                return str(param)

        # Patch Force Str With Fallback
        sql_module.force_str_with_fallback = force_str_with_fallback

    # Serialize Parameter
    def _serialize_param(self, param: object) -> str | None:
        """
        Attempt To Serialize Parameter To JSON String.

        Args:
            param (object): Parameter To Serialize.

        Returns:
            str | None: JSON String Or None If Serialization Fails.
        """

        # If Param Has Adapted Attribute
        if hasattr(param, "adapted"):
            # Return Serialized Adapted
            return self._serialize_adapted(param.adapted)

        # If Param Is Dict Or List
        if isinstance(param, (dict, list)):
            # Return JSON-Encoded Dict/List
            return json.dumps(param, cls=DjangoJSONEncoder)

        # If Param Has Class And Jsonb In Class Name
        if hasattr(param, "__class__") and "jsonb" in param.__class__.__name__.lower():
            # Return Serialized JSONB
            return self._serialize_jsonb(param)

        # Return None
        return None

    # Serialize Adapted
    def _serialize_adapted(self, adapted: Any) -> str | None:
        """
        Serialize Adapted Object.

        Args:
            adapted (Any): Adapted Object To Serialize.

        Returns:
            str | None: JSON String Or None If Serialization Fails.
        """

        try:
            # If Adapted Has Dumps Attribute
            if hasattr(adapted, "dumps"):
                # Return Serialized Adapted
                return adapted.dumps(adapted.adapted)

            # If Adapted Is Dict Or List
            if isinstance(adapted, (dict, list)):
                # Return JSON-Encoded Dict/List
                return json.dumps(adapted, cls=DjangoJSONEncoder)

            # Return String
            return str(adapted)

        except Exception:
            # Create Log Message
            log_message: str = f"Failed To Serialize Adapted Object: {adapted}"

            # Log Exception
            logger.exception(log_message)

            # Return None
            return None

    # Serialize JSONB
    def _serialize_jsonb(self, param: Any) -> str | None:
        """
        Serialize JSONB Object.

        Args:
            param (Any): JSONB Object To Serialize.

        Returns:
            str | None: JSON String Or None If Serialization Fails.
        """

        try:
            # If Param Has Obj Attribute
            if hasattr(param, "obj"):
                # Return JSON-Encoded Obj
                return json.dumps(param.obj, cls=DjangoJSONEncoder)

            # If Param Has Data Attribute
            if hasattr(param, "data"):
                # Return JSON-Encoded Data
                return json.dumps(param.data, cls=DjangoJSONEncoder)

        except Exception:
            # Create Log Message
            log_message: str = f"Failed To Serialize JSONB Object: {param}"

            # Log Exception
            logger.exception(log_message)

        # Return None
        return None

    # Patch Explain Query
    def _patch_explain_query(self, sql_module: Any) -> None:
        """
        Patch Silk's Explain Query Function For Safe JSON Handling.

        Args:
            sql_module (Any): Silk SQL Module To Patch.
        """

        # Explain Query
        def explain_query(connection: Any, query: str, params: Iterable[object]) -> list[tuple] | None:
            """
            Execute EXPLAIN With Safe JSON Parameter Handling.

            Args:
                connection (Any): Database Connection Object.
                query (str): SQL Query String Without EXPLAIN Prefix.
                params (Iterable[object]): SQL Parameters For The Query.

            Returns:
                list[tuple] | None: Result Rows Or None If Failed.
            """

            try:
                # Sanitize Parameters
                safe_params = [self._sanitize_param(param) for param in params]

                # With Connection Cursor
                with connection.cursor() as cur:
                    # Prefixed Query
                    prefixed_query: str = f"EXPLAIN {query}"

                    # Log Debug
                    logger.debug(
                        "Executing EXPLAIN Query",
                        extra={"query": prefixed_query, "params": safe_params},
                    )

                    # Execute Query
                    cur.execute(prefixed_query, tuple(safe_params))

                    # Return Fetched All
                    return cur.fetchall()

            except Exception:
                # Create Log Message
                log_message: str = "EXPLAIN Query Failed; Returning None To Preserve Flow"

                # Log Exception
                logger.exception(log_message)

                # Return None
                return None

        # Patch Explain Query
        sql_module._explain_query = explain_query  # noqa: SLF001

    # Sanitize Parameter
    def _sanitize_param(self, param: object) -> object:
        """
        Sanitize Parameter For Safe SQL Execution.

        Args:
            param (object): Parameter To Sanitize.

        Returns:
            object: Sanitized Parameter.
        """
        # Serialize Parameter
        serialized = self._serialize_param(param)

        # If Serialized Is Not None
        if serialized is not None:
            # Return Serialized
            return serialized

        # If Param Has Adapted Attribute
        if hasattr(param, "adapted"):
            # Return String Adapted
            return str(param.adapted)

        # Return Param
        return param


# Exports
__all__: list[str] = ["CommonConfig"]
