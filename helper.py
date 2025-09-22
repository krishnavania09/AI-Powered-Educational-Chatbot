# helper.py
import os
import pickle
import traceback
from typing import Optional

MODEL_PATH = os.getenv("LOCAL_MODEL_PATH", "model.pkl")
VECTORIZER_PATH = os.getenv("LOCAL_VECTORIZER_PATH", "vectorizer.pkl")

model = None
vectorizer = None

def _load_local_artifacts():
    global model, vectorizer
    try:
        with open(MODEL_PATH, "rb") as mf:
            model = pickle.load(mf)
    except FileNotFoundError:
        print("⚠️  model.pkl not found – running in LLM-only mode.")
        model = None
    except Exception as e:
        print(f"⚠️  Failed to load model.pkl ({e}) – falling back to LLM-only mode.")
        model = None

    try:
        with open(VECTORIZER_PATH, "rb") as vf:
            vectorizer = pickle.load(vf)
    except FileNotFoundError:
        if model is not None:
            print("⚠️  vectorizer.pkl not found – local model will be disabled.")
        vectorizer = None
    except Exception as e:
        print(f"⚠️  Failed to load vectorizer.pkl ({e}) – disabling local model.")
        vectorizer = None

_load_local_artifacts()

def local_predict(user_text: str) -> Optional[str]:
    try:
        if model is None or vectorizer is None:
            return None
        X = vectorizer.transform([user_text])
        pred = getattr(model, "predict", None)
        if pred is None:
            return None
        y = model.predict(X)
        return str(y[0])
    except Exception:
        print("⚠️  local_predict failed, falling back to LLM.\n" + traceback.format_exc())
        return None

def _call_openai_chat(messages, model_name: Optional[str] = None) -> str:
    model_name = model_name or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "[Configuration error] OPENAI_API_KEY is not set."

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.2,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e_new:
        try:
            import openai
            openai.api_key = api_key
            resp = openai.ChatCompletion.create(
                model=model_name,
                messages=messages,
                temperature=0.2,
            )
            return resp["choices"][0]["message"]["content"].strip()
        except Exception as e_old:
            return (f"[LLM error] Unable to call OpenAI API.\nNew SDK error: {e_new}\nLegacy SDK error: {e_old}")

def send_gptnew(user_text: str, system_prompt: Optional[str] = None) -> str:
    local_answer = local_predict(user_text)
    if local_answer:
        return local_answer

    system_prompt = system_prompt or (
        "You are a helpful educational assistant. "
        "Answer clearly and concisely. If code is shown, format it properly."
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_text},
    ]
    return _call_openai_chat(messages)

def answer_user(user_text: str) -> str:
    return send_gptnew(user_text)
