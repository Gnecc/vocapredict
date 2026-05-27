import React, { useEffect, useMemo, useState } from "react";
import {
    IonPage, IonHeader, IonToolbar, IonTitle, IonContent,
    IonList, IonItem, IonLabel, IonNote, IonBadge,
    IonButton, IonCard, IonCardHeader, IonCardTitle,
    IonCardContent, IonProgressBar, useIonRouter, IonToast, IonSpinner
} from "@ionic/react";
import { loadResponses, clearResponses } from "../storage";

const API_BASE_URL = process.env.REACT_APP_API_URL || "https://macso-patient-dream-1724.fly.dev";
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

function aggregateByCategory(responses) {
    const map = new Map();
    for (const r of responses) {
        const key = r.category || "Desconocida";
        if (!map.has(key)) map.set(key, []);
        if (typeof r.value === "number" && r.value >= 1 && r.value <= 5) {
            map.get(key).push(r.value);
        }
    }
    const out = [];
    for (const [category, values] of map.entries()) {
        const count = values.length;
        const sum = values.reduce((a, b) => a + b, 0);
        const avg = count ? sum / count : 0;
        const pctOfMax = count ? sum / (count * 5) : 0; // 0..1
        out.push({ category, count, sum, avg, pctOfMax });
    }
    out.sort((a, b) => b.avg - a.avg || b.pctOfMax - a.pctOfMax);
    return out;
}

const CATEGORY_ORDER = [
    "Cálculo",
    "C. Físico",
    "C. Biológico",
    "Mecánico",
    "S. Social",
    "Literario",
    "Persuasivo",
    "Artístico",
    "Musical",
];

const CATEGORY_ALIASES = {
    "Servicio Social": "S. Social",
};

function getNormalizedScore(row) {
    return row.pctOfMax ?? 0;
}

function buildScoresPayload(aggregates) {
    const byName = new Map();
    for (const row of aggregates) {
        const normalizedName = CATEGORY_ALIASES[row.category] || row.category;
        byName.set(normalizedName, getNormalizedScore(row));
    }
    const scores = CATEGORY_ORDER.map(cat =>
        Number((byName.get(cat) ?? 0).toFixed(2))
    );
    return { scores };
}

export default function Results() {
    const router = useIonRouter();
    const [responses, setResponses] = useState(loadResponses);
    const [sending, setSending] = useState(false);
    const [toast, setToast] = useState({ open: false, msg: "" });

    useEffect(() => {
        setResponses(loadResponses());
    }, []);

    const aggregates = useMemo(() => aggregateByCategory(responses), [responses]);

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

            const payload = buildScoresPayload(aggregates);

            const res = await fetch(PREDICT_URL, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });

            const data = await res.json().catch(() => ({}));

            localStorage.setItem("last_prediction", JSON.stringify({
                prediction: data?.prediction ?? null,
                probabilities: data?.probabilities ?? null
            }));

            router.push("/prediction", {
                state: {
                    prediction: data?.prediction ?? null,
                    probabilities: data?.probabilities ?? null
                }
            });

        } catch (err) {
            console.error("Error /predict:", err);
            setToast({ open: true, msg: "Error al analizar datos." });
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

            <IonContent className="ion-padding">
                <IonCard>
                    <IonCardHeader>
                        <IonCardTitle>Resumen general</IonCardTitle>
                    </IonCardHeader>
                    <IonCardContent>
                        <IonNote>
                            Respuestas registradas: <strong>{totalAnswered}</strong>
                        </IonNote>
                        <br/>
                        <IonNote>
                            Escala: 1 = “Me desagrada mucho”, 5 = “Me gusta mucho”.
                        </IonNote>
                    </IonCardContent>
                </IonCard>

                <IonList>
                    {aggregates.map((row) => (
                        <IonItem key={row.category} lines="full" className="ion-text-wrap">
                            <IonLabel>
                                <h2 style={{marginBottom: 6}}>
                                    {row.category}{" "}
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

                {!aggregates.length && (
                    <IonCard>
                        <IonCardContent>
                            <p>No hay respuestas guardadas. Realiza el cuestionario primero.</p>
                        </IonCardContent>
                    </IonCard>
                )}

                <div className="ion-padding">
                    <IonButton
                        expand="block"
                        fill="solid"
                        onClick={handleAnalyze}
                        disabled={sending}
                    >
                        {sending ? <IonSpinner name="dots"/> : 'Analizar datos'}
                    </IonButton>
                </div>

                <div className="ion-padding">
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
            </IonContent>
        </IonPage>
    );
}
