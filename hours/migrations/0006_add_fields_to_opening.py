# Generated by Django 3.0.2 on 2020-06-02 09:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('hours', '0005_add_daily_hours_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='dailyhours',
            name='last_modified_time',
            field=models.DateTimeField(auto_now=True, db_index=True, null=True),
        ),
        migrations.AddField(
            model_name='opening',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='hours_opening_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='opening',
            name='created_time',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='opening',
            name='last_modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='hours_opening_modified_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='opening',
            name='last_modified_time',
            field=models.DateTimeField(auto_now=True, db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name='opening',
            name='status',
            field=models.IntegerField(choices=[(0, 'closed'), (1, 'open'), (2, 'undefined'), (3, 'self_service'), (4, 'with key'), (5, 'with reservation'), (6, 'with key and reservation'), (7, 'only entering'), (8, 'only leaving')], db_index=True, default=1),
        ),
        migrations.AlterField(
            model_name='period',
            name='status',
            field=models.IntegerField(choices=[(0, 'closed'), (1, 'open'), (2, 'undefined'), (3, 'self_service'), (4, 'with key'), (5, 'with reservation'), (6, 'with key and reservation'), (7, 'only entering'), (8, 'only leaving')], db_index=True, default=1),
        ),
        migrations.AlterField(
            model_name='target',
            name='default_status',
            field=models.IntegerField(choices=[(0, 'closed'), (1, 'open'), (2, 'undefined'), (3, 'self_service'), (4, 'with key'), (5, 'with reservation'), (6, 'with key and reservation'), (7, 'only entering'), (8, 'only leaving')], default=2),
        ),
        migrations.AlterField(
            model_name='target',
            name='target_type',
            field=models.IntegerField(choices=[(0, 'unit'), (1, 'unit_service'), (2, 'special_group'), (3, 'person'), (4, 'telephone'), (5, 'service'), (6, 'service_channel'), (7, 'service_at_unit'), (8, 'resource'), (9, 'building'), (10, 'area')], default=0),
        ),
    ]
