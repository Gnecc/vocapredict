import {
    IonBadge, IonCard, IonCardContent, IonCardHeader, IonCardSubtitle, IonCardTitle,
    IonCol, IonContent, IonGrid, IonHeader, IonPage, IonRow, IonTitle, IonToolbar
} from '@ionic/react';

import styles from "./Quiz.module.scss";
import React, { useMemo, useRef, useState } from 'react';

import { Answer } from '../components/Answer';
import { CompletedCard } from '../components/CompletedCard';
import { QuizStats } from '../components/QuizStats';
import { saveResponse } from "../storage";
import { MOCK_QUESTIONS } from "../questions";

export default function Questions() {
    const completionContainerRef = useRef(null);

    const questions = useMemo(() => MOCK_QUESTIONS || [], []);
    const [currentIndex, setCurrentIndex] = useState(0);
    const [completed, setCompleted] = useState(false);
    const [answering, setAnswering] = useState(false);
    const [selectedAnswer, setSelectedAnswer] = useState(null);

    const handleAnswerClick = (event, answerKey, question) => {
        if (answering) return;

        setAnswering(true);
        setSelectedAnswer(answerKey);

        const value = question.likertMap?.[answerKey] ?? null;
        saveResponse({
            questionId: question.id,
            question: question.question,
            category: question.category ?? null,
            answerKey,
            answerLabel: question.answers?.[answerKey],
            value,
            ts: Date.now(),
        });

        setTimeout(() => {
            if (currentIndex >= questions.length - 1) {
                setCompleted(true);
                setAnswering(false);
                setSelectedAnswer(null);
                return;
            }
            setCurrentIndex(index => index + 1);
            setAnswering(false);
            setSelectedAnswer(null);
        }, 600);
    };

    const currentQuestion = questions[currentIndex];

    return (
        <IonPage>
            <IonHeader className={styles.questionHeader}>
                <IonToolbar>
                    <IonTitle className={styles.logoTitle}>
                        <img src="/assets/logo.png" className={styles.questionLogo} alt="VocaPredict" />
                    </IonTitle>
                </IonToolbar>
            </IonHeader>

            <IonContent fullscreen className="background">
                {!completed && currentQuestion && (
                    <IonGrid className={styles.mainGrid}>
                        <QuizStats
                            questionsLength={questions.length}
                            currentQuestion={currentIndex + 1}
                        />

                        <IonRow className={styles.mainRow}>
                            <IonCol size="12">
                                <IonCard id="questionCard">
                                    <IonCardHeader className="ion-text-center">
                                        <IonCardSubtitle>{currentQuestion.category}</IonCardSubtitle>
                                        <IonBadge color="success">Likert</IonBadge>
                                        <IonCardTitle className={styles.questionTitle}>
                                            {currentQuestion.question}
                                        </IonCardTitle>
                                    </IonCardHeader>

                                    <IonCardContent>
                                        {Object.keys(currentQuestion.answers)
                                            .filter(answerKey => currentQuestion.answers[answerKey] !== null)
                                            .map(answerKey => (
                                                <Answer
                                                    key={answerKey}
                                                    answer={answerKey}
                                                    question={currentQuestion}
                                                    handleAnswerClick={handleAnswerClick}
                                                    disabled={answering}
                                                    selected={selectedAnswer === answerKey}
                                                />
                                            ))}
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
