import pandas as pd

avaliacoes = {
    'criterio1': {
        'monotonico': 1,
        'valores': {
            'a1': 2,
            'a2': 3,
            'a3': 4
        }
    },
    'criterio2': {
        'monotonico': 0,
        'valores': {
            'a1': 2,
            'a2': 3,
            'a3': 4
        }
    },
}

df = pd.DataFrame([avaliacao['valores'] for avaliacao in avaliacoes.values()],
                  index=avaliacoes.keys())

print(df)
