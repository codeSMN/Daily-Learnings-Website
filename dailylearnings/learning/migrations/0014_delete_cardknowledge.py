# Generated by Django 4.0 on 2021-12-27 13:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0013_alter_profile_bio_alter_profile_fav_subject_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CardKnowledge',
        ),
    ]