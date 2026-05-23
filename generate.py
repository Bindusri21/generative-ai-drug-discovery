import numpy as np
import joblib

from tensorflow.keras.models import load_model
from rdkit import Chem

# =========================
# LOAD MODEL
# =========================

model = load_model("models/drug_model.h5")

char_to_idx = joblib.load("models/char_to_idx.pkl")
idx_to_char = joblib.load("models/idx_to_char.pkl")

# =========================
# SEED
# =========================

seed = "CCOCCCCCCCCCCCCCCCC"

generated = seed

# =========================
# GENERATE MOLECULE
# =========================

for _ in range(50):

    try:

        x_pred = np.array([
            [char_to_idx[c] for c in seed]
        ])

        prediction = model.predict(
            x_pred,
            verbose=0
        )

        next_index = np.argmax(prediction)

        next_char = idx_to_char[next_index]

        generated += next_char

        seed = generated[-20:]

    except:
        break

print("\nGenerated Molecule:\n")
print(generated)

# =========================
# VALIDATION
# =========================

mol = Chem.MolFromSmiles(generated)

if mol:
    print("\nValid Molecule")
else:
    print("\nInvalid Molecule")
