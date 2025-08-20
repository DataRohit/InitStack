# ruff: noqa: PLC0415

# Standard Library Imports
import logging
from collections.abc import Iterable
from typing import Any

# Third Party Imports
from django.apps import AppConfig
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

        # Apply Silk Patches To Fix JSON Serialization Issues
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
    def _patch_silk_json_handling(self) -> None:  # noqa: C901, PLR0915
        """
        Patch Silk JSON Handling To Prevent Jsonb Serialization Issues.
        """

        try:
            # Standard Library Imports
            import json

            # Third Party Imports
            from django.core.serializers.json import DjangoJSONEncoder

            # Monkey Patch Force Str Fallback
            def patched_force_str_with_fallback(param: object) -> str:  # noqa: C901, PLR0911
                """
                Convert Arbitrary Parameter To String With JSON Safety.

                Args:
                    param (object): Arbitrary Parameter To Convert.

                Returns:
                    str: Converted String Representation.
                """

                # If Adapted Attribute Exists
                if hasattr(param, "adapted"):
                    # If Adapted Has Dumps Method
                    if hasattr(param.adapted, "dumps"):
                        try:
                            # Try To Serialize Using Adapted Object
                            return param.adapted.dumps(param.adapted.adapted)

                        except Exception:
                            # Create Log Message
                            log_message: str = f"Failed To Serialize Adapted Object: {param.adapted}"

                            # Log Exception
                            logger.exception(log_message)

                    # If Adapted Is Dict Or List
                    elif isinstance(param.adapted, (dict, list)):
                        # Serialize Using JSON Encoder
                        return json.dumps(param.adapted, cls=DjangoJSONEncoder)

                    else:
                        # Return String Representation
                        return str(param.adapted)

                # If Param Is Dict Or List
                if isinstance(param, (dict, list)):
                    # Serialize Using JSON Encoder
                    return json.dumps(param, cls=DjangoJSONEncoder)

                # If Param Has Class And JSONB In Class Name
                if hasattr(param, "__class__") and "jsonb" in param.__class__.__name__.lower():
                    try:
                        # If Param Has Obj Attribute
                        if hasattr(param, "obj"):
                            # Serialize Using JSON Encoder
                            return json.dumps(param.obj, cls=DjangoJSONEncoder)

                        # If Param Has Data Attribute
                        if hasattr(param, "data"):
                            # Serialize Using JSON Encoder
                            return json.dumps(param.data, cls=DjangoJSONEncoder)

                    except Exception:
                        # Create Log Message
                        log_message: str = f"Failed To Serialize JSONB Object: {param}"

                        # Log Exception
                        logger.exception(log_message)

                try:
                    # Third Party Import
                    from silk.utils.encoding import force_str

                    # Return Force Str Result
                    return force_str(param)

                except ImportError:
                    # Return String Representation
                    return str(param)

            # Third Party Import
            import silk.sql

            # Apply Force Str Fallback Patch
            silk.sql.force_str_with_fallback = patched_force_str_with_fallback

            # Patch Explain Query Safely
            def patched_explain_query(
                connection: Any,
                query: str,
                params: Iterable[object],
            ) -> list[tuple] | None:
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
                    # Initialize Safe Params List
                    safe_params: list[object] = []

                    # Iterate Over Params
                    for param in params:
                        # Check If Param Is Jsonb Object
                        if hasattr(param, "__class__") and "jsonb" in param.__class__.__name__.lower():
                            try:
                                # If Param Has Obj Attribute
                                if hasattr(param, "obj"):
                                    # Append JSON-Encoded Obj
                                    safe_params.append(json.dumps(param.obj, cls=DjangoJSONEncoder))

                                else:
                                    # Append Empty JSON Fallback
                                    safe_params.append(str(param.obj) if hasattr(param, "obj") else "{}")

                            except Exception:
                                # Create Log Message
                                log_message: str = f"Failed To Sanitize JSONB Param: {param}"

                                # Log Exception
                                logger.exception(log_message)

                                # Append Empty JSON Fallback
                                safe_params.append("{}")

                        # Check If Param Is Dict Or List
                        elif isinstance(param, (dict, list)):
                            # Append JSON-Encoded Dict/List
                            safe_params.append(json.dumps(param, cls=DjangoJSONEncoder))

                        # Check If Param Has Adapted Attribute
                        elif hasattr(param, "adapted"):
                            # Check If Adapted Is Dict Or List
                            if isinstance(param.adapted, (dict, list)):
                                # Append JSON-Encoded Adapted Value
                                safe_params.append(json.dumps(param.adapted, cls=DjangoJSONEncoder))

                            else:
                                # Append String Adapted Value
                                safe_params.append(str(param.adapted))

                        else:
                            # Append Raw Param
                            safe_params.append(param)

                    with connection.cursor() as cur:
                        # Build EXPLAIN-Prefixed Query
                        prefixed_query: str = f"EXPLAIN {query}"

                        # Debug Log Execution Details
                        logger.debug(
                            "Executing EXPLAIN Query",
                            extra={
                                "query": prefixed_query,
                                "params": safe_params,
                            },
                        )

                        # Execute EXPLAIN Statement
                        cur.execute(prefixed_query, tuple(safe_params))

                        # Fetch All Rows
                        return cur.fetchall()

                except Exception:
                    # Create Log Message
                    log_message: str = "EXPLAIN Query Failed; Returning None To Preserve Flow"

                    # Log Exception
                    logger.exception(log_message)

                    # Silently Fail EXPLAIN Queries To Avoid Breaking The Main Flow
                    return None

            # Apply Explain Query Patch
            silk.sql._explain_query = patched_explain_query  # noqa: SLF001

        except ImportError:
            # Create Log Message
            log_message: str = "Silk Not Installed; Skipping EXPLAIN Query Patch"

            # Log Exception
            logger.exception(log_message)

        except Exception:
            # Create Log Message
            log_message: str = "EXPLAIN Query Patch Failed; Continuing Without Patch"

            # Log Exception
            logger.exception(log_message)


# Exports
__all__: list[str] = ["CommonConfig"]
