# Generated by Django 4.0.3 on 2022-08-03 16:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0008_order_shop'),
    ]

    operations = [
        migrations.AddField(
            model_name='shopowner',
            name='address',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]