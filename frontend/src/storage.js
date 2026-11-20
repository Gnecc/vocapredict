// Keep the previous Hereford responses untouched when switching instruments.
const KEY = 'quiz_responses_riasec_v1';

export function loadResponses() {
    try {
        return JSON.parse(localStorage.getItem(KEY)) ?? [];
    } catch {
        return [];
    }
}

export function saveResponse(entry) {
    const prev = loadResponses().filter(r => r.questionId !== entry.questionId);
    const all = [...prev, entry];
    localStorage.setItem(KEY, JSON.stringify(all));
    return all;
}

export function clearResponses() {
    localStorage.removeItem(KEY);
}
