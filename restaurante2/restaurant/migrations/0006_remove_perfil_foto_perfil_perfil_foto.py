# Generated by Django 5.2 on 2025-06-03 23:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0005_remove_almuerzo_informacion_almuerzo_precio_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='perfil',
            name='foto_perfil',
        ),
        migrations.AddField(
            model_name='perfil',
            name='foto',
            field=models.ImageField(blank=True, null=True, upload_to='perfil/'),
        ),
    ]
