from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0007_multiplos_decisores"),
    ]

    operations = [
        migrations.AddField(
            model_name="projeto",
            name="resultado_gerado_em",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
