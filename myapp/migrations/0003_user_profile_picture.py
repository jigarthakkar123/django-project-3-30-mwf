# Generated by Django 5.0.2 on 2024-03-06 10:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_user_usertype'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='profile_picture',
            field=models.ImageField(default='', upload_to='profile_picture/'),
        ),
    ]
