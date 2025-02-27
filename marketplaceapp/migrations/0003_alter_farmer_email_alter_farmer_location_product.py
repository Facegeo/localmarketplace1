# Generated by Django 4.2 on 2024-11-30 15:50

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('marketplaceapp', '0002_customer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='farmer',
            name='email',
            field=models.EmailField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='farmer',
            name='location',
            field=models.CharField(max_length=250),
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('quantity', models.PositiveIntegerField()),
                ('product_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='product_images/')),
                ('farmer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='marketplaceapp.farmer')),
            ],
        ),
    ]
