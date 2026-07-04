import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ideas", "0006_alter_idea_interest"),
    ]

    operations = [
        migrations.AlterField(
            model_name="idea",
            name="interest",
            field=models.PositiveIntegerField(
                default=0,
                validators=[django.core.validators.MinValueValidator(0)],
                verbose_name="관심도",
            ),
        ),
    ]
