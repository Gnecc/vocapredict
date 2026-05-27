import { IonButton, IonCard, IonCardContent, IonCardHeader, IonCardTitle, IonCol, IonGrid, IonRow, useIonRouter } from "@ionic/react";

export const CompletedCard = ({ completionContainerRef }) => {

    const router = useIonRouter();

    const playAgain = () => {
        router.push("/");
    }

    return (
        <IonGrid ref={ completionContainerRef }>
            <IonRow className="ion-text-center">
                <IonCol size="12">
                    <IonCard>
                        <IonCardHeader>
                            <IonCardTitle>Cuestionario completado</IonCardTitle>
                        </IonCardHeader>

                        <IonCardContent>
                            <IonButton expand="block" onClick={() => router.push("/results")}>
                                Ver resultados
                            </IonButton>
                            <IonButton expand="block" fill="outline" onClick={playAgain}>
                                Volver al inicio
                            </IonButton>
                        </IonCardContent>
                    </IonCard>
                </IonCol>
            </IonRow>
        </IonGrid>
    );
}
