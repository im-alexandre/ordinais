import secrets

from django.db import migrations, models
from django.db.models import deletion

import core.models


def _gerar_token_unico(apps, schema_editor):
    Decisor = apps.get_model("core", "Decisor")
    tokens_existentes = set(
        Decisor.objects.exclude(token__isnull=True).values_list("token",
                                                                flat=True))

    for decisor in Decisor.objects.filter(token__isnull=True).order_by("id"):
        token = secrets.token_urlsafe(24)
        while token in tokens_existentes:
            token = secrets.token_urlsafe(24)
        decisor.token = token
        decisor.save(update_fields=["token"])
        tokens_existentes.add(token)


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0006_projeto_data"),
    ]

    operations = [
        migrations.AddField(
            model_name="decisor",
            name="token",
            field=models.CharField(
                blank=True,
                null=True,
                editable=False,
                max_length=64,
            ),
        ),
        migrations.AddField(
            model_name="decisor",
            name="status",
            field=models.CharField(
                choices=[
                    ("pendente", "Pendente"),
                    ("em_edicao", "Em edicao"),
                    ("concluido", "Concluido"),
                    ("desativado", "Desativado"),
                ],
                default="pendente",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="decisor",
            name="ativo",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="decisor",
            name="is_criador",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="decisor",
            name="criado_em",
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AddField(
            model_name="decisor",
            name="concluido_em",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="decisor",
            name="desativado_em",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="alternativacriterio",
            name="decisor",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=deletion.CASCADE,
                related_name="alternativacriterios",
                to="core.decisor",
            ),
        ),
        migrations.RunPython(_gerar_token_unico, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="decisor",
            name="token",
            field=models.CharField(
                default=core.models.gerar_token_decisor,
                editable=False,
                max_length=64,
                unique=True,
            ),
        ),
    ]
