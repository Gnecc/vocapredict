import React from "react";
import {
    IonPage, IonHeader, IonToolbar, IonTitle, IonContent,
    IonCard, IonCardHeader, IonCardTitle, IonCardContent,
    IonList, IonItem, IonLabel, IonBadge, IonButtons, IonButton, IonIcon, useIonRouter
} from "@ionic/react";
import { homeOutline, analyticsOutline } from "ionicons/icons";

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
    // state inyectado por Results.jsx (router.push)
    const nav = router.routeInfo?.state ?? {};
    const prediction = nav?.prediction ?? loadLastPrediction()?.prediction ?? null;
    const probabilities = nav?.probabilities ?? loadLastPrediction()?.probabilities ?? null;

    return (
        <IonPage>
            <IonHeader>
                <IonToolbar>
                    <IonTitle>Predicción del modelo</IonTitle>
{/*
                    <IonButtons slot="end">
                        <IonButton onClick={() => router.push("/results")} title="Ver resultados">
                            <IonIcon icon={analyticsOutline} />
                        </IonButton>
                        <IonButton onClick={() => router.push("/")} title="Inicio">
                            <IonIcon icon={homeOutline} />
                        </IonButton>
                    </IonButtons>
*/}
                </IonToolbar>
            </IonHeader>

            <IonContent className="ion-padding">
                <IonCard className="animate__animated animate__fadeInUp">
                    <IonCardHeader>
                        <IonCardTitle>
                            {"Predicción."}
                        </IonCardTitle>
                    </IonCardHeader>
                    <IonCardContent>
                        {probabilities ? (
                            <>
                                <p>Probabilidades por clase:</p>
                                <IonList>
                                    {Object.entries(probabilities)
                                        .sort((a,b) => b[1]-a[1])
                                        .map(([label, p]) => (
                                            <IonItem key={label}>
                                                <IonLabel>{label}</IonLabel>
                                                <IonBadge color="primary">{(p*100).toFixed(1)}%</IonBadge>
                                            </IonItem>
                                        ))}
                                </IonList>
                            </>
                        ) : (
                            <p>El servicio no devolvió probabilidades. Solo se muestra la clase predicha.</p>
                        )}

                        <div style={{ marginTop: 16, display: "flex", gap: 8 }}>
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
