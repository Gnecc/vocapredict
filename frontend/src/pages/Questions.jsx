import {
    IonBadge, IonCard, IonCardContent, IonCardHeader, IonCardSubtitle, IonCardTitle,
    IonButton, IonCol, IonContent, IonGrid, IonHeader, IonInput, IonItem, IonNote, IonPage, IonProgressBar, IonRow, IonToolbar,
    useIonViewWillEnter
} from '@ionic/react';

import styles from "./Quiz.module.scss";
import React, { useEffect, useMemo, useRef, useState } from 'react';

import { Answer } from '../components/Answer';
import { CompletedCard } from '../components/CompletedCard';
import { saveResponse } from "../storage";
import { MOCK_QUESTIONS } from "../questions";

const DISPLAY_AREAS = {
    "Cálculo": "Cálculo",
    "C. Físico": "Científico-física",
    "C. Biológico": "Científico-biológica",
    "Mecánico": "Mecánica",
    "Servicio Social": "Servicio social",
    "Literario": "Literaria",
    "Persuasivo": "Persuasiva",
    "Artístico": "Artística",
    "Musical": "Musical",
};

export default function Questions() {
    const completionContainerRef = useRef(null);
    const sessionKeyRef = useRef("");

    const questions = useMemo(() => MOCK_QUESTIONS || [], []);
    const [currentIndex, setCurrentIndex] = useState(0);
    const [completed, setCompleted] = useState(false);
    const [answering, setAnswering] = useState(false);
    const [selectedAnswer, setSelectedAnswer] = useState(null);
    const [inputValue, setInputValue] = useState("");

    const resetQuestionnaire = () => {
        setCurrentIndex(0);
        setCompleted(false);
        setAnswering(false);
        setSelectedAnswer(null);
        setInputValue("");
    };

    useEffect(resetQuestionnaire, []);

    useIonViewWillEnter(() => {
        const sessionKey = window.location.search;
        if (sessionKey && sessionKey !== sessionKeyRef.current) {
            sessionKeyRef.current = sessionKey;
            resetQuestionnaire();
        }
    });

    const moveNext = () => {
        if (currentIndex >= questions.length - 1) {
            setCompleted(true);
            setAnswering(false);
            setSelectedAnswer(null);
            return;
        }
        setCurrentIndex(index => index + 1);
        setAnswering(false);
        setSelectedAnswer(null);
        setInputValue("");
    };

    const handleAnswerClick = (event, answerKey, question) => {
        if (answering) return;

        if (question.multiple) {
            setSelectedAnswer(current => {
                const selected = Array.isArray(current) ? current : [];
                return selected.includes(answerKey)
                    ? selected.filter(key => key !== answerKey)
                    : [...selected, answerKey];
            });
            return;
        }

        setAnswering(true);
        setSelectedAnswer(answerKey);

        const value = question.likertMap?.[answerKey] ?? null;
        saveResponse({
            questionId: question.id,
            question: question.question,
            category: question.category ?? null,
            type: question.type ?? "hereford",
            amaiKey: question.amaiKey ?? null,
            answerKey,
            answerLabel: question.answers?.[answerKey],
            value,
            ts: Date.now(),
        });

        setTimeout(moveNext, 600);
    };

    const handleMultipleContinue = question => {
        const selected = Array.isArray(selectedAnswer) ? selectedAnswer : [];
        if (!selected.length) return;

        saveResponse({
            questionId: question.id,
            question: question.question,
            category: question.category ?? null,
            type: question.type ?? "hereford",
            amaiKey: question.amaiKey ?? null,
            answerKey: selected.join("|"),
            answerLabel: selected.map(key => question.answers?.[key]).join("; "),
            value: selected.map(key => question.answers?.[key]),
            ts: Date.now(),
        });
        moveNext();
    };

    const handleInputContinue = question => {
        const value = String(inputValue).trim();
        if (!question.optional && !value) return;

        saveResponse({
            questionId: question.id,
            question: question.question,
            category: question.category ?? null,
            type: question.type ?? "hereford",
            amaiKey: question.amaiKey ?? null,
            answerKey: "input",
            answerLabel: value,
            value,
            ts: Date.now(),
        });
        moveNext();
    };

    const currentQuestion = questions[currentIndex];
    const isSocioeconomic = currentQuestion?.type === "socioeconomic";
    const isFirstSocioeconomic = isSocioeconomic && questions[currentIndex - 1]?.type !== "socioeconomic";
    const areaLabel = DISPLAY_AREAS[currentQuestion?.category] || currentQuestion?.category;
    const progress = questions.length ? (currentIndex + 1) / questions.length : 0;

    return (
        <IonPage>
            <IonHeader className={styles.questionHeader}>
                <IonToolbar>
                    <div className={styles.headerShell}>
                        <img src="/assets/logo-home.png" className={styles.questionLogo} alt="VocaPredict" />
                        <div className={styles.headerMeta}>
                            <span>{isSocioeconomic ? "Estudio socioeconómico" : "Inventario Hereford"}</span>
                            <strong>{Math.min(currentIndex + 1, questions.length)} / {questions.length}</strong>
                        </div>
                    </div>
                    <IonProgressBar value={progress} className={styles.headerProgress} />
                </IonToolbar>
            </IonHeader>

            <IonContent fullscreen className="background">
                {!completed && currentQuestion && (
                    <IonGrid className={styles.mainGrid}>
                        <IonRow className={styles.mainRow}>
                            <IonCol size="12">
                                <IonCard id="questionCard">
                                    <IonCardHeader className="ion-text-center">
                                        <IonCardSubtitle>
                                            {isSocioeconomic ? "Sección final" : "Área de interés"}
                                        </IonCardSubtitle>
                                        <IonBadge color="success">
                                            {isSocioeconomic ? "Socioeconómico" : areaLabel}
                                        </IonBadge>
                                        {isFirstSocioeconomic && (
                                            <p className={styles.sectionIntro}>
                                                Terminaste el inventario principal. Ahora responde este breve bloque
                                                socioeconómico para complementar la sugerencia.
                                            </p>
                                        )}
                                        <IonCardTitle className={styles.questionTitle}>
                                            {currentQuestion.question}
                                        </IonCardTitle>
                                    </IonCardHeader>

                                    <IonCardContent>
                                        {currentQuestion.input && (
                                            <>
                                                <IonItem>
                                                    <IonInput
                                                        value={inputValue}
                                                        placeholder={currentQuestion.optional ? "Opcional" : "Escribe tu respuesta"}
                                                        onIonChange={event => setInputValue(event.detail.value ?? "")}
                                                    />
                                                </IonItem>
                                                <IonButton
                                                    expand="block"
                                                    onClick={() => handleInputContinue(currentQuestion)}
                                                    disabled={!currentQuestion.optional && !String(inputValue).trim()}
                                                >
                                                    Continuar
                                                </IonButton>
                                            </>
                                        )}
                                        {!currentQuestion.input && Object.keys(currentQuestion.answers)
                                                .filter(answerKey => currentQuestion.answers[answerKey] !== null)
                                                .map(answerKey => (
                                                    <Answer
                                                        key={answerKey}
                                                        answer={answerKey}
                                                        question={currentQuestion}
                                                        handleAnswerClick={handleAnswerClick}
                                                        disabled={answering}
                                                        selected={
                                                            currentQuestion.multiple
                                                                ? Array.isArray(selectedAnswer) && selectedAnswer.includes(answerKey)
                                                                : selectedAnswer === answerKey
                                                        }
                                                    />
                                                ))}
                                        {currentQuestion.multiple && (
                                            <>
                                                <IonNote>Selecciona una o más opciones.</IonNote>
                                                <IonButton
                                                    expand="block"
                                                    onClick={() => handleMultipleContinue(currentQuestion)}
                                                    disabled={!Array.isArray(selectedAnswer) || !selectedAnswer.length}
                                                >
                                                    Continuar
                                                </IonButton>
                                            </>
                                        )}
                                    </IonCardContent>
                                </IonCard>
                            </IonCol>
                        </IonRow>
                    </IonGrid>
                )}

                {completed && (
                    <CompletedCard
                        completionContainerRef={completionContainerRef}
                    />
                )}
            </IonContent>
        </IonPage>
    );
}
