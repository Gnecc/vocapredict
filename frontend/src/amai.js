const AMAI_MAX_SCORE = 300;

const EDUCATION_POINTS = {
    "Sin instrucción": 0,
    "Primaria incompleta": 6,
    "Primaria completa": 11,
    "Secundaria incompleta": 12,
    "Secundaria completa": 18,
    "Carrera comercial": 23,
    "Carrera técnica": 23,
    "Preparatoria incompleta": 23,
    "Preparatoria completa": 27,
    "Licenciatura incompleta": 36,
    "Licenciatura completa": 59,
    "Diplomado o maestría": 85,
    "Doctorado": 85,
};

function countValue(value) {
    const raw = String(value ?? "").toLowerCase();
    if (raw.includes("más") || raw.includes("mas") || raw.includes("o más")) {
        const match = raw.match(/\d+/);
        return match ? Number(match[0]) : 4;
    }
    return Number(raw);
}

function getAnswer(responses, questionId) {
    return responses.find(response => response.questionId === questionId)?.answerLabel;
}

function classify(score) {
    if (score >= 202) return "A/B";
    if (score >= 168) return "C+";
    if (score >= 141) return "C";
    if (score >= 116) return "C-";
    if (score >= 95) return "D+";
    if (score >= 48) return "D";
    return "E";
}

export function calculateAmai(responses) {
    const education = getAnswer(responses, "socio_head_education");
    const bathrooms = countValue(getAnswer(responses, "socio_bathrooms"));
    const cars = countValue(getAnswer(responses, "socio_cars"));
    const internet = getAnswer(responses, "socio_internet");
    const workers = countValue(getAnswer(responses, "socio_workers"));
    const bedrooms = countValue(getAnswer(responses, "socio_bedrooms"));

    if (!education || !internet || [bathrooms, cars, workers, bedrooms].some(Number.isNaN)) {
        return null;
    }

    const score =
        (EDUCATION_POINTS[education] ?? 0) +
        (bathrooms === 0 ? 0 : bathrooms === 1 ? 24 : 47) +
        (cars === 0 ? 0 : cars === 1 ? 22 : 43) +
        (internet === "Si" ? 32 : 0) +
        ({ 0: 0, 1: 15, 2: 31, 3: 46 }[workers] ?? 61) +
        ({ 0: 0, 1: 8, 2: 16, 3: 24 }[bedrooms] ?? 32);

    return {
        score,
        level: classify(score),
        normalized: Number((score / AMAI_MAX_SCORE).toFixed(6)),
    };
}
