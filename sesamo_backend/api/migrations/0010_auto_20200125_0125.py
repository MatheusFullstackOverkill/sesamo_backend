# Generated by Django 3.0.2 on 2020-01-25 04:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_auto_20200125_0124'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Client'),
        ),
    ]
