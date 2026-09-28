from __future__ import annotations

from functools import lru_cache

from .config import get_settings


class FitnessAI:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._model = None
        self._flash_model = None
        if self.settings.google_api_key:
            import google.generativeai as genai

            genai.configure(api_key=self.settings.google_api_key)
            self._model = genai.GenerativeModel(self.settings.workout_model)
            self._flash_model = genai.GenerativeModel(self.settings.nutrition_model)

    @property
    def live(self) -> bool:
        return self._model is not None

    def generate_workout(self, *, age: int, weight: float, goal: str, intensity: str) -> str:
        prompt = f"""You are a careful fitness coach. Create a safe, structured 7-day workout plan.
User: age {age}, weight {weight} kg, goal {goal}, intensity {intensity}.
For every day include a focus, 5-10 minute warm-up, exercises with sets/reps or duration,
and a cooldown or recovery note. Include rest days where appropriate. Be concise, clear,
and advise consulting a clinician for medical limitations. Do not prescribe medical treatment."""
        if self._model:
            return self._generate(self._model, prompt)
        return self._demo_plan(goal, intensity)

    def generate_nutrition_tip(self, goal: str) -> str:
        prompt = f"Give one concise, practical nutrition or recovery tip for a fitness goal of {goal}. Avoid medical claims."
        if self._flash_model:
            return self._generate(self._flash_model, prompt)
        return f"Build meals around your {goal} goal: include a protein source, colorful produce, and enough water, then adjust portions to your energy needs."

    def update_workout(self, original_plan: str, feedback: str) -> str:
        prompt = f"""Revise this 7-day workout plan according to the user's feedback.
Keep the day-by-day format, preserve useful details, and prioritize safety.
Original plan:\n{original_plan}\n\nFeedback:\n{feedback}"""
        if self._model:
            return self._generate(self._model, prompt)
        return f"UPDATED PLAN\n\nApplied feedback: {feedback}\n\n{original_plan}"

    @staticmethod
    def _generate(model: object, prompt: str) -> str:
        response = model.generate_content(prompt)
        text = getattr(response, "text", "").strip()
        if not text:
            raise RuntimeError("The AI provider returned an empty response")
        return text

    @staticmethod
    def _demo_plan(goal: str, intensity: str) -> str:
        days = [
            ("Day 1", "Full-body strength", "Squats 3x10; push-ups 3x8; rows 3x10"),
            ("Day 2", "Cardio", "Brisk walk or cycle 25 minutes; mobility 10 minutes"),
            ("Day 3", "Lower body", "Lunges 3x10/side; glute bridges 3x12; calf raises 3x15"),
            ("Day 4", "Active recovery", "Easy walk 20 minutes; gentle stretching 10 minutes"),
            ("Day 5", "Upper body and core", "Shoulder press 3x10; incline push-ups 3x8; plank 3x30 seconds"),
            ("Day 6", "Intervals", "Six rounds: 1 minute brisk effort and 2 minutes easy recovery"),
            ("Day 7", "Rest and reset", "Rest, hydrate, and prepare for the next week"),
        ]
        sections = [f"7-DAY {intensity.upper()} PLAN | GOAL: {goal}", "Warm-up each training day: 5-10 minutes of easy movement."]
        sections += [f"{day}: {focus}\nWorkout: {workout}\nCooldown: 5 minutes of easy stretching." for day, focus, workout in days]
        sections.append("Safety: use controlled form, stop for sharp pain, and scale volume to your experience.")
        return "\n\n".join(sections)


@lru_cache
def get_fitness_ai() -> FitnessAI:
    return FitnessAI()
