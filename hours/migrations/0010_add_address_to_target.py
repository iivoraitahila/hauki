# Generated by Django 3.0.7 on 2020-09-23 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("hours", "0009_add_extra_identifiers_for_targets"),
    ]

    operations = [
        migrations.AddField(
            model_name="target",
            name="address",
            field=models.TextField(
                blank=True, default="", verbose_name="Street address"
            ),
        ),
    ]
