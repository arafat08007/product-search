# Generated by Django 3.0.7 on 2020-06-05 01:31

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MapPoint',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('product', models.CharField(max_length=288)),
                ('lat', models.DecimalField(decimal_places=3, max_digits=10)),
                ('long', models.DecimalField(decimal_places=3, max_digits=10)),
            ],
        ),
    ]
