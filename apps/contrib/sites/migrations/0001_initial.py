import django.contrib.sites.models
from django.contrib.sites.models import _simple_domain_name_validator
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Site",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "domain",
                    models.CharField(
                        max_length=100,
                        verbose_name="Domain Name",
                        validators=[_simple_domain_name_validator],
                    ),
                ),
                ("name", models.CharField(max_length=50, verbose_name="Display Name")),
            ],
            options={
                "ordering": ("domain",),
                "db_table": "django_site",
                "verbose_name": "Site",
                "verbose_name_plural": "Sites",
            },
            bases=(models.Model,),
            managers=[("objects", django.contrib.sites.models.SiteManager())],
        ),
    ]
