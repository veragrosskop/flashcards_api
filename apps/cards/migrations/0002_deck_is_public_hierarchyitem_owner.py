import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("cards", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="deck",
            name="is_public",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="hierarchyitem",
            name="owner",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="hierarchy_items",
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
    ]
