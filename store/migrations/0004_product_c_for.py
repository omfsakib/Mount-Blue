# Generated by Django 4.0.2 on 2022-07-21 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_product_featured_alter_product_category_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='c_for',
            field=models.CharField(blank=True, choices=[('Woman', 'Woman'), ('Man', 'Man')], max_length=200, null=True),
        ),
    ]