# Generated by Django 5.0.2 on 2024-03-13 00:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0005_delete_bid_delete_comment'),
    ]

    operations = [
        migrations.RenameField(
            model_name='category',
            old_name='category',
            new_name='cname',
        ),
    ]
