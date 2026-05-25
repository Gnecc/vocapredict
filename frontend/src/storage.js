const KEY = 'quiz_responses';

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
