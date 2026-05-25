import {
    IonBadge, IonCard, IonCardContent, IonCardHeader, IonCardSubtitle, IonCardTitle,
    IonCol, IonContent, IonGrid, IonHeader, IonPage, IonRow, IonTitle, IonToolbar,
    useIonRouter, useIonViewDidEnter
} from '@ionic/react';

import styles from "./Quiz.module.scss";
import { useStoreState } from 'pullstate';
import { SettingsStore } from '../store';
import { getChosenCategory, getChosenDifficulty } from '../store/Selectors';
import React, { useEffect, useRef, useState } from 'react';

import { Swiper, SwiperSlide } from 'swiper/react';
import 'swiper/swiper.scss';

import { Answer } from '../components/Answer';
import { CompletedCard } from '../components/CompletedCard';
import { QuizStats } from '../components/QuizStats';

// 👇 importa el mock que ya generamos con las 90 preguntas
import { MOCK_QUESTIONS} from "../questions";

const STORAGE_KEY = "quiz_responses";

function saveResponse(entry) {
    const prev = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]")
        .filter(r => r.questionId !== entry.questionId);
    const all = [...prev, entry];
    localStorage.setItem(STORAGE_KEY, JSON.stringify(all));
    return all;
}

export default function Questions() {
    const mainContainerRef = useRef(null);
    const completionContainerRef = useRef(null);
    const swiperRef = useRef(null);

    const router = useIonRouter();
    const chosenCategory = useStoreState(SettingsStore, getChosenCategory);
    const chosenDifficulty = useStoreState(SettingsStore, getChosenDifficulty);

    const [currentQuestion, setCurrentQuestion] = useState(1);
    const [score, setScore] = useState(0);
    const [completed, setCompleted] = useState(false);
    const [questions, setQuestions] = useState([]); // ✅ ahora sí existe setQuestions
    const [slideSpace, setSlideSpace] = useState(0);

    useEffect(() => {
        // carga inicial desde el mock
        setQuestions(MOCK_QUESTIONS || []);
    }, []);

    useIonViewDidEnter(() => {
        setSlideSpace(40);
    });

    const handleAnswerClick = (event, answerKey, question) => {
        // 1) feedback visual
        event?.target?.setAttribute?.("color", "success");

        // 2) valor likert
        const value = question.likertMap?.[answerKey] ?? null;

        // 3) guardar selección
        const entry = {
            questionId: question.id,
            question: question.question,
            category: question.category ?? null,
            answerKey,
            answerLabel: question.answers?.[answerKey],
            value,
            ts: Date.now(),
        };
        saveResponse(entry);

        // 4) avanzar
        setTimeout(() => {
            setScore(s => s + 1);
            event?.target?.setAttribute?.("color", "light");
            swiperRef.current?.swiper?.slideNext();
            checkIfComplete();
        }, 600);
    };

    const checkIfComplete = () => {
        if (currentQuestion === questions.length) {
            mainContainerRef.current?.classList?.add("animate__zoomOutDown");
            setTimeout(() => {
                setCompleted(true);
                completionContainerRef.current?.classList?.add("animate__zoomInUp");
            }, 1000);
        }
    };

    return (
        <IonPage>
            <IonHeader>
                <IonToolbar>
                    <IonTitle>
                        <img src="/assets/logo.png" style={{ width: "50%" }} alt="logo" />
                    </IonTitle>
                </IonToolbar>
            </IonHeader>

            <IonContent fullscreen className="background">
                {!completed && (
                    <IonGrid className={`${styles.mainGrid} animate__animated`} ref={mainContainerRef}>
                        <QuizStats
                            chosenCategory={chosenCategory}
                            chosenDifficulty={chosenDifficulty}
                            questionsLength={questions.length}
                            currentQuestion={currentQuestion}
                            score={score}
                        />

                        <IonRow className={styles.mainRow}>
                            <IonCol size="12">
                                <IonRow>
                                    <Swiper
                                        ref={swiperRef}
                                        spaceBetween={slideSpace}
                                        slidesPerView={1}
                                        onSlideChange={e => setCurrentQuestion(e.activeIndex + 1)}
                                    >
                                        {questions.map((question, qIndex) => (
                                            <SwiperSlide key={`question_${qIndex}`}>
                                                <IonCard id="questionCard" className="animate__animated">
                                                    <IonCardHeader className="ion-text-center">
                                                        <IonCardSubtitle>{question.category}</IonCardSubtitle>
                                                        {question?.tags?.length > 0 && (
                                                            <IonBadge color="success">
                                                                {question.tags[0].name}
                                                            </IonBadge>
                                                        )}
                                                        <IonCardTitle className={styles.questionTitle}>
                                                            {question.question}
                                                        </IonCardTitle>
                                                    </IonCardHeader>

                                                    <IonCardContent>
                                                        {Object.keys(question.answers).map((answerKey, aIndex) => {
                                                            if (question.answers[answerKey] !== null) {
                                                                return (
                                                                    <Answer
                                                                        key={`answer_${aIndex}`}
                                                                        answer={answerKey}
                                                                        question={question}
                                                                        handleAnswerClick={handleAnswerClick}
                                                                    />
                                                                );
                                                            }
                                                            return null;
                                                        })}
                                                    </IonCardContent>
                                                </IonCard>
                                            </SwiperSlide>
                                        ))}
                                    </Swiper>
                                </IonRow>
                            </IonCol>
                        </IonRow>
                    </IonGrid>
                )}

                {completed && (
                    <CompletedCard
                        completionContainerRef={completionContainerRef}
                        score={score}
                        questionsLength={questions.length}
                    />
                )}
            </IonContent>
        </IonPage>
    );
}
