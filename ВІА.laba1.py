import numpy as np
import pandas as pd
def calculate_distances(matrix: np.ndarray, p: float = 3.0) -> dict:
    x1, x2 = matrix[0], matrix[1]

    sq_euclidean = np.sum((x1 - x2) ** 2)
    euclidean = np.sqrt(sq_euclidean)
    chebyshev = np.max(np.abs(x1 - x2))
    minkowski = np.sum(np.abs(x1 - x2) ** p) ** (1 / p)
    return {
        "Відстань Евкліда": euclidean,
        "Квадрат відстані Евкліда": sq_euclidean,
        "Відстань Міньковського": minkowski,
        "Відстань Чебишова": chebyshev,
    }
feature_names = [
    "ЧашолисткаДовжинаСм",
    "Ширина чашолистка см",
    "Довжина пелюсткиСм",
    "Ширина пелюстки см",
]
iris_variant_18 = pd.DataFrame(
    [
        [18, 4.9, 3.1, 1.5, 0.1, "setosa"],  
        [18, 5.0, 3.2, 1.2, 0.2, "setosa"],  
    ],
    columns=["ID"] + feature_names + ["види"],
)
data_matrix = iris_variant_18[feature_names].to_numpy()
results = {}
for n in [2, 3, 4]:
    sub_matrix = data_matrix[:, :n]
    results[f"{n} ознаки"] = calculate_distances(sub_matrix)
df_results = pd.DataFrame(results)
print(df_results.round(4))