"""Score ten vocational families using the exported 48-answer Optuna ensemble."""

from itertools import combinations

import numpy as np
import pandas as pd


def family_scores(artifact, answers):
    items = pd.DataFrame(answers, columns=artifact["questions"])
    areas = pd.DataFrame(items.to_numpy().reshape(-1, 6, 8).mean(axis=2) / 5,
                         columns=artifact["areas"])
    with_areas = items.join(areas)
    interactions = {f"{a} {b}": areas[a] * areas[b] for a, b in combinations(areas, 2)}
    features = {"respuestas": items, "respuestas y áreas": with_areas,
                "interacciones": with_areas.join(pd.DataFrame(interactions))}
    career_scores = artifact["grouped"].predict_proba(items)
    grouped = career_scores @ artifact["memberships"]
    reference = (grouped + artifact["direct"].predict_proba(items)) / 2
    scores = [reference] + [model.predict_proba(features[key]) for key, model in artifact["candidates"]]
    return np.average(scores, axis=0, weights=artifact["weights"]) * artifact["prior_factor"]
