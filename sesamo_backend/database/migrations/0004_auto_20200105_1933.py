# Generated by Django 3.0 on 2020-01-05 22:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0003_auto_20200105_1755'),
    ]

    operations = [
        migrations.RenameField(
            model_name='faq',
            old_name='categoy',
            new_name='category',
        ),
    ]
