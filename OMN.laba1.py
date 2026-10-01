import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

file_name = "diabetes.tab_KP1.txt"

df = pd.read_csv(file_name, sep=r"\s+", na_values=["", "NA", "NaN"])

print("РОЗМІР ДАТАСЕТУ:")
print(df.shape)

print("\nНАЗВИ ОЗНАК:")
print(df.columns.tolist())

print("\nПЕРШІ 5 ПАЦІЄНТІВ:")
print(df.head(5).to_string(index=False))

print("\n" + "=" * 60)
print("2. ПРОПУЩЕНІ ЗНАЧЕННЯ")
print("=" * 60)

missing = df.isnull().sum()

print(missing)

print("\nЗагальна кількість пропущених значень:",
      missing.sum())

numeric_columns = df.columns

imputer = SimpleImputer(strategy="median")

df_imputed = pd.DataFrame(
    imputer.fit_transform(df[numeric_columns]),
    columns=numeric_columns
)

print("\nПропущені значення після імпутації:")
print(df_imputed.isnull().sum())

print("\nМетод імпутації: медіана.")

print(
    "Обґрунтування: медіана менш чутлива до викидів, "
    "ніж середнє арифметичне. Оскільки в медичних даних "
    "можуть бути екстремальні значення, використання медіани "
    "є доцільним."
)

print("\n" + "=" * 60)
print("3. СПІВВІДНОШЕННЯ SEX")
print("=" * 60)

sex_counts = df_imputed["SEX"].value_counts().sort_index()

print("SEX:")
print(sex_counts)

sex_percent = df_imputed["SEX"].value_counts(
    normalize=True
).sort_index() * 100

print("\nВідсоткове співвідношення:")
print(sex_percent.round(2))

print("\nПримітка:")
print("SEX = 1 — чоловіки")
print("SEX = 2 — жінки")

difference = abs(sex_percent.iloc[0] - sex_percent.iloc[1])

if difference < 10:
    print("\nВисновок: значного дисбалансу між чоловіками та жінками немає.")
else:
    print("\nВисновок: присутній певний дисбаланс між чоловіками та жінками.")

print("\n" + "=" * 60)
print("4. ВИКИДИ ЗА IQR")
print("=" * 60)

features = [
    "AGE",
    "BMI",
    "BP",
    "S1",
    "S2",
    "S3",
    "S4",
    "S5",
    "S6"
]

outlier_results = []

for column in features:

    Q1 = df_imputed[column].quantile(0.25)
    Q3 = df_imputed[column].quantile(0.75)

    IQR = Q3 - Q1

    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    outliers = df_imputed[
        (df_imputed[column] < lower_bound) |
        (df_imputed[column] > upper_bound)
    ]

    outlier_results.append([
        column,
        Q1,
        Q3,
        IQR,
        lower_bound,
        upper_bound,
        len(outliers)
    ])

outlier_table = pd.DataFrame(
    outlier_results,
    columns=[
        "Ознака",
        "Q1",
        "Q3",
        "IQR",
        "Нижня межа",
        "Верхня межа",
        "Кількість викидів"
    ]
)

print(outlier_table.to_string(index=False))

print("\n" + "=" * 60)
print("5. СТАНДАРТИЗАЦІЯ")
print("=" * 60)

features_10 = [
    "AGE",
    "SEX",
    "BMI",
    "BP",
    "S1",
    "S2",
    "S3",
    "S4",
    "S5",
    "S6"
]

scaler = StandardScaler()

df_scaled = df_imputed.copy()

df_scaled[features_10] = scaler.fit_transform(
    df_imputed[features_10]
)

print("Перші 5 пацієнтів після стандартизації:")
print(
    df_scaled[features_10 + ["Y"]]
    .head(5)
    .round(4)
    .to_string(index=False)
)


print("\n" + "=" * 60)
print("6. КОРЕЛЯЦІЙНА МАТРИЦЯ")
print("=" * 60)

correlation_matrix = df_imputed[features_10].corr()

print(
    correlation_matrix
    .round(3)
    .to_string()
)

print("\nСильно корельовані пари |r| > 0.7:")

strong_pairs = []

for i in range(len(features_10)):
    for j in range(i + 1, len(features_10)):

        r = correlation_matrix.iloc[i, j]

        if abs(r) > 0.7:
            strong_pairs.append(
                (features_10[i], features_10[j], r)
            )

if len(strong_pairs) == 0:
    print("Сильно корельованих пар не знайдено.")
else:
    for feature1, feature2, r in strong_pairs:
        print(
            f"{feature1} - {feature2}: r = {r:.3f}"
        )

df_imputed.to_csv(
    "diabetes_imputed.csv",
    index=False
)

df_scaled.to_csv(
    "diabetes_scaled.csv",
    index=False
)

correlation_matrix.to_csv(
    "correlation_matrix.csv"
)

outlier_table.to_csv(
    "outliers_IQR.csv",
    index=False
)

print("\n" + "=" * 60)
print("РОБОТУ ЗАВЕРШЕНО")
print("=" * 60)

print("""
Створені файли:

1. diabetes_imputed.csv
2. diabetes_scaled.csv
3. correlation_matrix.csv
4. outliers_IQR.csv
""")