# ruff: noqa: PLC0415

# Third Party imports
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _
from health_check.plugins import plugin_dir


# Common App Configuration Class
class CommonConfig(AppConfig):
    """
    Common App Configuration Class.

    Attributes:
        name (str): The Name Of The App.
        verbose_name (str): The Verbose Name Of The App.

    Methods:
        ready() -> None: Ready Function To Register The Health Check Backends.
    """

    # Attributes
    name: str = "apps.common"
    verbose_name: str = _("Common")

    # Ready Function
    def ready(self) -> None:
        """
        Ready Function To Register The Health Check Backends.
        """

        # Local Imports
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
