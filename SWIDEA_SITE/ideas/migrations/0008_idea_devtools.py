from django.db import migrations, models


def copy_devtool_to_devtools(apps, schema_editor):
    Idea = apps.get_model("ideas", "Idea")
    for idea in Idea.objects.exclude(devtool__isnull=True):
        idea.devtools.add(idea.devtool_id)


class Migration(migrations.Migration):
    dependencies = [
        ("ideas", "0007_alter_idea_interest"),
    ]

    operations = [
        migrations.AddField(
            model_name="idea",
            name="devtools",
            field=models.ManyToManyField(
                related_name="multi_ideas",
                to="ideas.devtool",
                verbose_name="개발툴",
            ),
        ),
        migrations.RunPython(copy_devtool_to_devtools, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="idea",
            name="devtool",
        ),
        migrations.AlterField(
            model_name="idea",
            name="devtools",
            field=models.ManyToManyField(
                related_name="ideas",
                to="ideas.devtool",
                verbose_name="개발툴",
            ),
        ),
    ]
