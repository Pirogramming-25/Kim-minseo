from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("ideas", "0004_idea_author"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="idea",
            name="status",
        ),
    ]
