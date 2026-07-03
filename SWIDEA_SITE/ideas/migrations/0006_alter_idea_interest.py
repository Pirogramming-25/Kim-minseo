import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ideas", "0005_remove_idea_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="idea",
            name="interest",
            field=models.PositiveIntegerField(
                default=0,
                validators=[django.core.validators.MinValueValidator(0)],
                verbose_name="우선순위 점수",
            ),
        ),
    ]
