import React, { useState } from "react";
import {
    IonPage, IonHeader, IonToolbar, IonTitle, IonContent,
    IonCard, IonCardHeader, IonCardTitle, IonCardContent,
    IonList, IonItem, IonLabel, IonButton, useIonRouter
} from "@ionic/react";
import styles from "./Prediction.module.scss";
import { clearResponses } from "../storage";

const STORAGE_KEY = "last_prediction_riasec_v1";
function loadLastPrediction() {
    try {
        return JSON.parse(localStorage.getItem(STORAGE_KEY)) ?? null;
    } catch {
        return null;
    }
}

function InterestNetwork({ connections }) {
    const [selectedCode, setSelectedCode] = useState(null);
    const selected = connections.find(connection => connection.career_code === selectedCode) ?? connections[0];

    return (
        <div className={styles.network}>
            <p>Elige una carrera para ver qué intereses la conectan con tu perfil.</p>
            <div className={styles.careerPicker} role="group" aria-label="Carreras conectadas con tus intereses">
                {connections.map(connection => (
                    <button
                        key={connection.career_code}
                        type="button"
                        aria-pressed={selected.career_code === connection.career_code}
                        onClick={() => setSelectedCode(connection.career_code)}
                    >
                        {connection.career_name}
                    </button>
                ))}
            </div>
            <div className={styles.connectionGraph} aria-live="polite">
                <strong className={styles.careerNode}>{selected.career_name}</strong>
                <ul key={selected.career_code} className={styles.interestNodes} aria-label="Intereses que respaldan la conexión">
                    {selected.interests.map(interest => (
                        <li key={interest.code}>
                            <strong>{interest.name} ({interest.code})</strong>
                            <span>{Math.round(interest.score * 100)}%</span>
                        </li>
                    ))}
                </ul>
            </div>
            <p className={styles.scoreNote}>Cada porcentaje corresponde a tu puntaje de interés en esa área.</p>
        </div>
    );
}

export default function Prediction() {
    const router = useIonRouter();
    const nav = router.routeInfo?.state ?? {};
    const result = nav?.recommendations ? nav : loadLastPrediction() ?? {};
    const recommendations = result.recommendations ?? [];
    const families = result.family_recommendations ?? [];
    const careersByFamily = result.careers_by_family;
    const connections = result.semantic_connections;

    const goHome = () => {
        clearResponses();
        localStorage.removeItem(STORAGE_KEY);
        router.push("/");
    };

    return (
        <IonPage>
            <IonHeader>
                <IonToolbar>
                    <IonTitle>Orientación vocacional</IonTitle>
                </IonToolbar>
            </IonHeader>

            <IonContent>
                <div className="vp-page-narrow">
                <IonCard className={styles.predictionCard}>
                    <IonCardHeader>
                        <IonCardTitle>
                            Opciones para explorar
                        </IonCardTitle>
                    </IonCardHeader>
                    <IonCardContent>
                        {families.length > 0 && (
                            <section className={styles.families}>
                                <h2>Familias vocacionales sugeridas</h2>
                                <ol>
                                    {families.map(family => (
                                        <li key={family}>
                                            <strong>{family}</strong>
                                            {careersByFamily?.[family]?.length > 0 && (
                                                <ul>
                                                    {careersByFamily[family].map(career => <li key={career}>{career}</li>)}
                                                </ul>
                                            )}
                                        </li>
                                    ))}
                                </ol>
                                {careersByFamily ? (
                                    <p>Las carreras de cada familia son opciones para explorar según tus respuestas.</p>
                                ) : (
                                    <p>Vuelve a analizar tus respuestas para ver carreras dentro de cada familia.</p>
                                )}
                            </section>
                        )}
                        {families.length === 0 && (recommendations.length ? (
                            <>
                                <p>El modelo relaciona tus respuestas con carreras que otras personas declararon estudiar. No predice satisfacción ni éxito profesional.</p>
                                <IonList className={styles.probabilityList}>
                                    {recommendations.slice(0, 3).map((recommendation, index) => {
                                        return (
                                            <IonItem key={recommendation.career_code} lines="none" className={styles.probabilityItem}>
                                                <IonLabel className={styles.probabilityContent}>
                                                    <div className={styles.probabilityHeader}>
                                                        <span className={styles.probabilityLabel}>
                                                            <strong>{index + 1}. {recommendation.career_name}</strong>
                                                        </span>
                                                    </div>
                                                </IonLabel>
                                            </IonItem>
                                        );
                                    })}
                                </IonList>
                            </>
                        ) : (
                            <p>No hay sugerencias guardadas. Completa el cuestionario y analiza tu perfil.</p>
                        ))}

                        {(Array.isArray(connections) || families.length > 0) && (
                            <section className={styles.families}>
                                <h2>Conexiones por intereses</h2>
                                {connections?.length > 0 ? (
                                    <InterestNetwork connections={connections} />
                                ) : (
                                    <p>{connections
                                        ? "La red encontró evidencia insuficiente para conectar tus intereses con una carrera de referencia."
                                        : "Vuelve a analizar tus respuestas para consultar las conexiones de la red semántica."}</p>
                                )}
                            </section>
                        )}

                        <div className={styles.predictionActions}>
                            <IonButton expand="block" onClick={() => router.push("/results")}>
                                Ver perfil / resultados
                            </IonButton>
                            <IonButton expand="block" fill="outline" onClick={goHome}>
                                Ir al inicio
                            </IonButton>
                        </div>
                    </IonCardContent>
                </IonCard>
                </div>
            </IonContent>
        </IonPage>
    );
}
