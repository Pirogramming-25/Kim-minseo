import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("ideas", "0003_ideastar_user_alter_session_key"),
    ]

    operations = [
        migrations.AddField(
            model_name="idea",
            name="author",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="ideas",
                to=settings.AUTH_USER_MODEL,
                verbose_name="작성자",
            ),
        ),
    ]
