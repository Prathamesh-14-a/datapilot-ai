from __future__ import annotations

from datetime import datetime

from src.database.crud import (
	get_ai_chat_sessions,
	get_analysis_history,
	get_job_fit_history,
	get_prediction_history,
	get_user_resumes,
)


def _safe_timestamp(item, *attribute_names):
	for attribute_name in attribute_names:
		value = getattr(item, attribute_name, None)
		if value:
			return value
	return datetime.min


def _format_lpa(value):
	if value is None:
		return None
	return round(float(value) / 100000, 1)


def build_dashboard_snapshot(user_id):
	resumes = get_user_resumes(user_id)
	analyses = sorted(
		get_analysis_history(user_id),
		key=lambda analysis: _safe_timestamp(analysis, "analysis_date"),
		reverse=True,
	)
	predictions = sorted(
		get_prediction_history(user_id),
		key=lambda prediction: _safe_timestamp(prediction, "prediction_date"),
		reverse=True,
	)
	job_fit_histories = sorted(
		get_job_fit_history(user_id),
		key=lambda history: _safe_timestamp(history, "created_at"),
		reverse=True,
	)
	chat_sessions = get_ai_chat_sessions(user_id)

	latest_analysis = analyses[0] if analyses else None
	latest_prediction = predictions[0] if predictions else None
	latest_resume = max(
		resumes,
		key=lambda resume: _safe_timestamp(resume, "uploaded_at"),
		default=None,
	)

	activity_items = []

	for resume in resumes:
		activity_items.append(
			{
				"kind": "Resume Upload",
				"title": resume.resume_name or "Uploaded resume",
				"detail": "Added to your resume library",
				"timestamp": _safe_timestamp(resume, "uploaded_at"),
			}
		)

	for analysis in analyses:
		ats_score = analysis.ats_score
		match_score = analysis.match_score
		activity_items.append(
			{
				"kind": "Resume Analysis",
				"title": analysis.target_role or "Resume analysis",
				"detail": (
					f"ATS {ats_score:.1f}% • Match {match_score:.1f}%"
					if ats_score is not None and match_score is not None
					else "Analysis saved to your history"
				),
				"timestamp": _safe_timestamp(analysis, "analysis_date"),
			}
		)

	for prediction in predictions:
		predicted_lpa = _format_lpa(prediction.predicted_salary)
		activity_items.append(
			{
				"kind": "Salary Prediction",
				"title": prediction.role or "Salary prediction",
				"detail": (
					f"Predicted {predicted_lpa:.1f} LPA"
					if predicted_lpa is not None
					else "Prediction saved to your history"
				),
				"timestamp": _safe_timestamp(prediction, "prediction_date"),
			}
		)

	for history in job_fit_histories:
		activity_items.append(
			{
				"kind": "Job Fit",
				"title": history.best_role or "Job fit result",
				"detail": (
					f"Best fit {history.best_score:.2f}%"
					if history.best_score is not None
					else "Job fit saved to your history"
				),
				"timestamp": _safe_timestamp(history, "created_at"),
			}
		)

	for chat_session in chat_sessions:
		activity_items.append(
			{
				"kind": "AI Mentor Chat",
				"title": chat_session.title or "AI Mentor conversation",
				"detail": "Conversation updated in your chat history",
				"timestamp": _safe_timestamp(chat_session, "updated_at", "created_at"),
			}
		)

	activity_items = sorted(
		activity_items,
		key=lambda item: item["timestamp"],
		reverse=True,
	)

	analysis_trend = [
		{
			"date": analysis.analysis_date,
			"ats_score": analysis.ats_score,
			"match_score": analysis.match_score,
			"role": analysis.target_role,
		}
		for analysis in reversed(analyses)
		if analysis.analysis_date is not None
	]

	salary_trend = [
		{
			"date": prediction.prediction_date,
			"salary_lpa": _format_lpa(prediction.predicted_salary),
			"role": prediction.role,
		}
		for prediction in reversed(predictions)
		if prediction.prediction_date is not None
	]

	return {
		"counts": {
			"resumes": len(resumes),
			"analyses": len(analyses),
			"predictions": len(predictions),
			"job_fit_history": len(job_fit_histories),
			"chats": len(chat_sessions),
		},
		"resumes": resumes,
		"analyses": analyses,
		"predictions": predictions,
		"job_fit_histories": job_fit_histories,
		"chat_sessions": chat_sessions,
		"activity_items": activity_items,
		"analysis_trend": analysis_trend,
		"salary_trend": salary_trend,
		"latest_analysis": latest_analysis,
		"latest_prediction": latest_prediction,
		"latest_resume": latest_resume,
	}	