import React from "react";
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

export default function Prediction() {
    const router = useIonRouter();
    const nav = router.routeInfo?.state ?? {};
    const result = nav?.recommendations ? nav : loadLastPrediction() ?? {};
    const recommendations = result.recommendations ?? [];
    const suggestedCareer = recommendations[0];

    const goHome = () => {
        clearResponses();
        localStorage.removeItem(STORAGE_KEY);
        router.push("/");
    };

    return (
        <IonPage>
            <IonHeader>
                <IonToolbar>
                    <IonTitle>Carreras sugeridas</IonTitle>
                </IonToolbar>
            </IonHeader>

            <IonContent>
                <div className="vp-page-narrow">
                <IonCard className={styles.predictionCard}>
                    <IonCardHeader>
                        <IonCardTitle>
                            Carreras sugeridas según tus intereses
                        </IonCardTitle>
                    </IonCardHeader>
                    <IonCardContent>
                        {suggestedCareer && (
                            <div className={styles.predictionHero}>
                                <span>Primera opción para explorar</span>
                                <strong>{suggestedCareer.career_name}</strong>
                            </div>
                        )}
                        {recommendations.length ? (
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
