import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("ideas", "0002_idea_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="ideastar",
            name="user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="idea_stars",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="ideastar",
            name="session_key",
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
        migrations.AddConstraint(
            model_name="ideastar",
            constraint=models.UniqueConstraint(
                fields=("idea", "user"),
                name="unique_idea_star_per_user",
            ),
        ),
    ]
