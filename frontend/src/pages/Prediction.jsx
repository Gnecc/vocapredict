import React from "react";
import {
    IonPage, IonHeader, IonToolbar, IonTitle, IonContent,
    IonCard, IonCardHeader, IonCardTitle, IonCardContent,
    IonList, IonItem, IonLabel, IonBadge, IonButton, useIonRouter
} from "@ionic/react";
import styles from "./Prediction.module.scss";

const STORAGE_KEY = "last_prediction";

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
    const prediction = nav?.prediction ?? loadLastPrediction()?.prediction ?? null;
    const probabilities = nav?.probabilities ?? loadLastPrediction()?.probabilities ?? null;
    const sortedProbabilities = probabilities
        ? Object.entries(probabilities).sort((a, b) => b[1] - a[1])
        : [];

    return (
        <IonPage>
            <IonHeader>
                <IonToolbar>
                    <IonTitle>Predicción del modelo</IonTitle>
                </IonToolbar>
            </IonHeader>

            <IonContent className="ion-padding">
                <IonCard className={styles.predictionCard}>
                    <IonCardHeader>
                        <IonCardTitle>
                            {"Predicción."}
                        </IonCardTitle>
                    </IonCardHeader>
                    <IonCardContent>
                        {probabilities ? (
                            <>
                                <p>Probabilidades por clase:</p>
                                <IonList className={styles.probabilityList}>
                                    {sortedProbabilities.map(([label, p]) => {
                                        const percent = Math.max(0, Math.min(100, p * 100));

                                        return (
                                            <IonItem key={label} lines="none" className={styles.probabilityItem}>
                                                <IonLabel className={styles.probabilityContent}>
                                                    <div className={styles.probabilityHeader}>
                                                        <span className={styles.probabilityLabel}>{label}</span>
                                                        <IonBadge className={styles.probabilityBadge}>
                                                            {percent.toFixed(1)}%
                                                        </IonBadge>
                                                    </div>
                                                    <div className={styles.probabilityTrack}>
                                                        <div
                                                            className={styles.probabilityBar}
                                                            style={{ width: `${percent}%` }}
                                                        />
                                                    </div>
                                                </IonLabel>
                                            </IonItem>
                                        );
                                    })}
                                </IonList>
                            </>
                        ) : (
                            <p>El servicio no devolvió probabilidades. Solo se muestra la clase predicha.</p>
                        )}

                        <div className={styles.predictionActions}>
                            <IonButton expand="block" onClick={() => router.push("/results")}>
                                Ver perfil / resultados
                            </IonButton>
                            <IonButton expand="block" fill="outline" onClick={() => router.push("/")}>
                                Ir al inicio
                            </IonButton>
                        </div>
                    </IonCardContent>
                </IonCard>
            </IonContent>
        </IonPage>
    );
}
