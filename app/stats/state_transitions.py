# app/state_management/state_transitions.py
from app.stats.question_stats import QuestionStates

STATE_TRANSITIONS = {
    "start": {"next": QuestionStates.waiting_for_question.state},

    QuestionStates.waiting_for_question.state: {
        "next": QuestionStates.waiting_for_creating_record_request.state,
        "back": "start"
    },

    QuestionStates.waiting_for_creating_record_request.state: {
        "next": QuestionStates.finish.state,
        "back": QuestionStates.waiting_for_creating_record_request.state,
        "cancel": "start"
    },
    QuestionStates.finish: {
    }
}
