from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("sites", "0003_set_site_domain_and_name"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="site",
            options={
                "ordering": ["domain"],
                "verbose_name": "Site",
                "verbose_name_plural": "Sites",
            },
        ),
    ]
