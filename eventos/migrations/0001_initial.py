# Generated by Django 5.0.6 on 2024-08-29 02:22

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('event_type', models.CharField(choices=[('personal', 'Personal'), ('company', 'Company')], max_length=20)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('funeraria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.funeraria')),
            ],
        ),
        migrations.CreateModel(
            name='EventAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignments', to='eventos.event')),
                ('worker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assigned_events', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]