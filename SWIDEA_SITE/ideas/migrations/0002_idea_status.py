from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ideas", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="idea",
            name="status",
            field=models.CharField(
                choices=[
                    ("planning", "구상중"),
                    ("developing", "개발중"),
                    ("done", "완료"),
                    ("paused", "보류"),
                ],
                default="planning",
                max_length=20,
                verbose_name="상태",
            ),
        ),
    ]
