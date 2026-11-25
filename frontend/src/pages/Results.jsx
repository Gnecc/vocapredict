import React, { useEffect, useMemo, useState } from "react";
import {
    IonPage, IonHeader, IonToolbar, IonTitle, IonContent,
    IonList, IonItem, IonLabel, IonNote, IonBadge,
    IonButton, IonCard, IonCardHeader, IonCardTitle,
    IonCardContent, IonProgressBar, useIonRouter, useIonViewWillEnter, IonToast, IonSpinner
} from "@ionic/react";
import { loadResponses, clearResponses } from "../storage";
import { RIASEC_AREAS, RIASEC_QUESTIONS } from "../questions/riasec";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8080";
const PREDICT_URL = `${API_BASE_URL.replace(/\/$/, "")}/predict`;

function toCSV(rows) {
    if (!rows.length) return "";
    const headers = Object.keys(rows[0]);
    const escape = (v) => {
        if (v == null) return "";
        const s = String(v);
        return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
    };
    const lines = [
        headers.join(","),
        ...rows.map((r) => headers.map((h) => escape(r[h])).join(","))
    ];
    return lines.join("\n");
}

const AREA_LABELS = { R: "Realista", I: "Investigador", A: "Artístico", S: "Social", E: "Emprendedor", C: "Convencional" };

function indexedAnswers(responses) {
    const validIds = new Set(RIASEC_QUESTIONS.map(question => question.id));
    return new Map(responses.filter(response =>
        response.type === "riasec" && validIds.has(response.questionId) &&
        Number.isInteger(response.value) && response.value >= 1 && response.value <= 5
    ).map(response => [response.questionId, response.value]));
}

function aggregateByCategory(byId) {
    return RIASEC_AREAS.map(category => {
        const values = Array.from({ length: 8 }, (_, index) => byId.get(`${category}${index + 1}`)).filter(value => value != null);
        const count = values.length;
        const sum = values.reduce((a, b) => a + b, 0);
        return { category, count, sum, avg: count ? sum / count : 0, pctOfMax: count ? sum / (count * 5) : 0 };
    });
}

export default function Results() {
    const router = useIonRouter();
    const [responses, setResponses] = useState(loadResponses);
    const [sending, setSending] = useState(false);
    const [toast, setToast] = useState({ open: false, msg: "" });

    useEffect(() => { setResponses(loadResponses()); }, []);
    useIonViewWillEnter(() => { setResponses(loadResponses()); });

    const byId = useMemo(() => indexedAnswers(responses), [responses]);
    const aggregates = useMemo(() => aggregateByCategory(byId), [byId]);
    const complete = aggregates.every(area => area.count === 8);

    const handleClear = () => {
        clearResponses();
        setResponses([]);
    };

    const handleExportCSV = () => {
        const csv = toCSV(responses);
        const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        const date = new Date().toISOString().slice(0, 19).replace(/[:T]/g, "-");
        a.href = url;
        a.download = `quiz_responses_${date}.csv`;
        a.click();
        URL.revokeObjectURL(url);
    };

    const handleAnalyze = async () => {
        try {
            setSending(true);

            if (!complete) {
                setToast({ open: true, msg: "Responde las 48 actividades antes de analizar tus intereses." });
                return;
            }

            const payload = {
                scores: aggregates.map(area => Number(area.pctOfMax.toFixed(6))),
                answers: RIASEC_QUESTIONS.map(question => byId.get(question.id)),
            };

            const res = await fetch(PREDICT_URL, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });

            const data = await res.json().catch(() => ({}));
            if (!res.ok || !Array.isArray(data.recommendations) || !data.recommendations.length) {
                throw new Error(data.detail || "El servicio no devolvió carreras sugeridas.");
            }

            localStorage.setItem("last_prediction_riasec_v1", JSON.stringify(data));
            router.push("/prediction");

        } catch (err) {
            console.error("Error /predict:", err);
            setToast({ open: true, msg: err.message || "Error al analizar datos." });
        } finally {
            setSending(false);
        }
    };


    const totalAnswered = responses.length;

    return (
        <IonPage>
            <IonHeader>
                <IonToolbar>
                    <IonTitle>Resultados</IonTitle>
                </IonToolbar>
            </IonHeader>

            <IonContent>
                <div className="vp-page-shell">
                <IonCard>
                    <IonCardHeader>
                        <IonCardTitle className="vp-section-title">Resumen general</IonCardTitle>
                    </IonCardHeader>
                    <IonCardContent>
                        <IonNote>
                            Respuestas registradas: <strong>{totalAnswered}</strong>
                        </IonNote>
                        <br/>
                        <IonNote className="vp-muted">
                            Escala: 1 = “Me desagrada mucho”, 5 = “Me gusta mucho”.
                        </IonNote>
                        <p className="vp-muted">
                            Los valores resumen tus respuestas en las seis áreas RIASEC. Son intereses expresados,
                            no medidas de habilidad ni equivalencias con el cuestionario Hereford.
                        </p>
                    </IonCardContent>
                </IonCard>

                <IonList className="vp-card-grid">
                    {aggregates.map((row) => (
                        <IonItem key={row.category} lines="full" className="ion-text-wrap">
                            <IonLabel>
                                <h2 style={{marginBottom: 6}}>
                                    {AREA_LABELS[row.category]} ({row.category}){" "}
                                    <IonBadge color="primary" style={{verticalAlign: "middle"}}>
                                        n={row.count}
                                    </IonBadge>
                                </h2>
                                <div style={{margin: "6px 0 10px"}}>
                                    <IonProgressBar value={row.pctOfMax}/>
                                </div>
                                <p>
                                    Promedio: <strong>{row.avg.toFixed(2)}</strong> &nbsp;|&nbsp; Suma:{" "}
                                    <strong>{row.sum}</strong> &nbsp;|&nbsp; % Máximo:{" "}
                                    <strong>{Math.round(row.pctOfMax * 100)}%</strong>
                                </p>
                            </IonLabel>
                        </IonItem>
                    ))}
                </IonList>

                {!responses.length && (
                    <IonCard>
                        <IonCardContent>
                            <p>No hay respuestas guardadas. Realiza el cuestionario primero.</p>
                        </IonCardContent>
                    </IonCard>
                )}

                <div className="vp-actions">
                    <IonButton
                        expand="block"
                        fill="solid"
                        onClick={handleAnalyze}
                        disabled={sending || !complete}
                    >
                        {sending ? <IonSpinner name="dots"/> : 'Analizar datos'}
                    </IonButton>
                </div>

                <div className="vp-actions">
                    <IonButton expand="block" fill="outline" onClick={handleExportCSV} disabled={!responses.length}>
                        Exportar respuestas CSV
                    </IonButton>
                    <IonButton expand="block" fill="clear" color="danger" onClick={handleClear} disabled={!responses.length}>
                        Borrar respuestas
                    </IonButton>
                </div>

                <IonToast
                    isOpen={toast.open}
                    message={toast.msg}
                    duration={2200}
                    position="bottom"
                    onDidDismiss={() => setToast({open: false, msg: ""})}
                />
                </div>
            </IonContent>
        </IonPage>
    );
}
