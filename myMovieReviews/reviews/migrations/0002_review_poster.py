from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reviews", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="review",
            name="poster",
            field=models.FileField(
                blank=True, upload_to="posters/", verbose_name="포스터"
            ),
        ),
    ]
