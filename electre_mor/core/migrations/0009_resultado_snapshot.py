from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0008_resultado_persistente"),
    ]

    operations = [
        migrations.AddField(
            model_name="projeto",
            name="resultado_snapshot",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
