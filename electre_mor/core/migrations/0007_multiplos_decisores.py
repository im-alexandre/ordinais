from django.db import migrations, models
from django.db.models import deletion

import core.models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0006_projeto_data"),
    ]

    operations = [
        migrations.AddField(
            model_name="decisor",
            name="token",
            field=models.CharField(
                default=core.models.gerar_token_decisor,
                editable=False,
                max_length=64,
                unique=True,
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
    ]
