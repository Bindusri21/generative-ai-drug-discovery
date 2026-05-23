import os
import pandas as pd
import numpy as np
import joblib

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense

# =========================
# CREATE MODELS FOLDER
# =========================

os.makedirs("models", exist_ok=True)

# =========================
# =========================
# LOAD DATASET (auto-detect common paths)
# =========================

def find_dataset():
    candidates = [
        "data/molecules.csv",
        "data/train.csv",
        "data/dataset_v1.csv",
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None

data_path = find_dataset()
if data_path is None:
    raise FileNotFoundError("No dataset found. Put a CSV at data/molecules.csv or data/train.csv")

df = pd.read_csv(data_path)
print(f"\nDataset Loaded Successfully from: {data_path}\n")
print(df.head())

# =========================
# FIND SMILES COLUMN
# =========================

possible_cols = [
    "SMILES",
    "smiles",
    "canonical_smiles"
]

smiles_col = None

for col in possible_cols:

    if col in df.columns:

        smiles_col = col
        break

if smiles_col is None:

    raise Exception(
        "SMILES column not found in dataset"
    )

# =========================
# USE SMALL DATA FOR SPEED
# =========================

smiles = (
    df[smiles_col]
    .dropna()
    .astype(str)
    .tolist()[:500]
)

print("\nTotal Molecules:", len(smiles))


# =========================
# TOKENIZATION
# =========================

chars = sorted(list(set(''.join(smiles))))

char_to_idx = {
    c:i for i,c in enumerate(chars)
}

idx_to_char = {
    i:c for c,i in char_to_idx.items()
}

print("\nVocabulary Size:", len(chars))

# =========================
# CREATE TRAINING DATA
# =========================


# sequence length used for training (must be set before building the model)
seq_length = 20

X = []
y = []

for smile in smiles:

    if len(smile) <= seq_length:
        continue

    for i in range(len(smile)-seq_length):

        seq = smile[i:i+seq_length]

        target = smile[i+seq_length]

        X.append(
            [char_to_idx[c] for c in seq]
        )

        y.append(
            char_to_idx[target]
        )

X = np.array(X)

y = np.array(y)

print("\nTraining Shape:", X.shape)

# =========================
# BUILD MODEL
# =========================

model = Sequential([

    Embedding(input_dim=len(chars), output_dim=64, input_length=seq_length),

    LSTM(64),

    Dense(
        len(chars),
        activation='softmax'
    )

])

# =========================
# COMPILE MODEL
# =========================

model.compile(

    loss='sparse_categorical_crossentropy',

    optimizer='adam',

    metrics=['accuracy']

)

print("\nModel Created Successfully\n")

# =========================
# TRAIN MODEL
# =========================

model.fit(

    X,

    y,

    epochs=1,

    batch_size=64

)

# =========================
# SAVE MODEL
# =========================

model.save(
    "models/drug_model.h5"
)

joblib.dump(

    char_to_idx,

    "models/char_to_idx.pkl"

)

joblib.dump(

    idx_to_char,

    "models/idx_to_char.pkl"

)

print(
    "\nTraining Completed Successfully"
)
