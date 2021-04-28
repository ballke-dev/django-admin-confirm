# Generated by Django 3.1.7 on 2021-03-26 01:30

from django.db import migrations, models
from ..validators import validate_currency


class Migration(migrations.Migration):

    dependencies = [
        ("market", "0010_checkout_itemsale_transaction"),
    ]

    operations = [
        migrations.AddField(
            model_name="itemsale",
            name="quantity",
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name="transaction",
            name="date",
            field=models.DateTimeField(default=None),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="itemsale",
            name="currency",
            field=models.CharField(max_length=5, validators=[validate_currency]),
        ),
    ]