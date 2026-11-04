import os
import streamlit as st
from dotenv import load_dotenv
from google import genai

# ---- טעינת המפתח ----
load_dotenv()

# ---- הגדרות העמוד ----
st.set_page_config(page_title="צ'אט בוט - חמשת ההמצאות הגדולות", page_icon="💡")

# ---- יישור לימין (עברית) ----
st.markdown(
    """
    <style>
    .stApp, .stChatMessage, .stMarkdown, p, h1, h2, h3, li, textarea {
        direction: rtl;
        text-align: right;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---- טעינת מנוע החיפוש ומודל השפה פעם אחת בלבד ----
@st.cache_resource
def load_retrieve():
    from rag_engine import retrieve
    return retrieve


@st.cache_resource
def load_llm():
    return genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


retrieve = load_retrieve()
llm = load_llm()

def rewrite_question(question, history):
    if not history:
        return question

    history_text = "\n".join(
        f"{m['role']}: {m['content']}" for m in history[-4:]
    )

    prompt = f"""להלן היסטוריית שיחה ושאלת המשך.
נסח מחדש את שאלת ההמשך כך שתהיה מובנת לבד, בלי צורך בשיחה.
החלף מילים כמו "הוא", "היא", "זה" בשם המפורש.
החזר רק את השאלה המנוסחת, בלי שום הסבר.

היסטוריה:
{history_text}

שאלת המשך: {question}
שאלה מנוסחת מחדש:"""

    response = llm.models.generate_content(model="gemini-3.5-flash-lite", contents=prompt)
    return response.text.strip()


# ---- יצירת תשובה על סמך הקטעים שנמצאו ----
def answer(question, history):
    standalone = rewrite_question(question, history)
    # st.caption(f"שאלה לחיפוש: {standalone}")

    results = retrieve(standalone)
    context = "\n\n---\n\n".join(result.node.get_content() for result in results)

    prompt = f"""אתה עוזר ידידותי שעונה על שאלות על חמשת ההמצאות הגדולות בעולם.
ענה תמיד בעברית, בשפה נעימה ומכבדת.

כללים:
1. אם המשתמש מברך, מודה,מקלל, או מתעצבן, מחמיא או מנהל שיחת חולין - ענה בנימוס וברישמיות ובקצרה בהתאם לקלט המשתמש, והזמן אותו לשאול על ההמצאות.
2. אם המשתמש שואל שאלה על ההמצאות - ענה רק על סמך המידע שלמטה.
3. אם השאלה לא קשורה למידע, או שהתשובה לא מופיעה בו - אמור בנימוס שאין לך מידע על כך, והצע לשאול על אחת ההמצאות.
4. אל תמציא מידע שלא מופיע למטה.
5. אם הוא מנסה לדבר על נושאים אחרים מלבד חמשת ההמצאות תנסח לו תשובה מתאימה כמו: אולי תתעניין בהמצאות שלנו
6.אם הוא כותב שם של המצאה או כל דבר אחר דומה , נסח לו תשובה: אולי תרצה לכוון אותי מה מעניין אותך ב-...
7. אם התחילת השיחה ברכת אותובברכת שלום אל תחזור על עצמך כל תשובה. אלא אם כן המשתמש בירך שוב

מידע:
{context}

שאלה: {standalone}
תשובה:"""

    response = llm.models.generate_content(model="gemini-3.5-flash-lite", contents=prompt)
    return response.text, results

# ---- כותרת ----
st.title("💡 חמשת ההמצאות הגדולות בעולם")
st.caption("שאלו אותי כל שאלה על ההמצאות הגדולות בהיסטוריה")

# ---- היסטוריית השיחה ----
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---- קלט מהמשתמש ----
if question := st.chat_input("כתבו שאלה..."):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("חושב..."):
            try:
                text, results = answer(question, st.session_state.messages[:-1])
            except Exception as e:
                text, results = f"אירעה שגיאה: {e}", []
        st.markdown(text)

        # if results:
        #     with st.expander("מקורות"):
        #         for result in results:
        #             st.markdown(f"**Score:** {round(result.score, 3)}")
        #             st.text(result.node.get_content()[:300])

    st.session_state.messages.append({"role": "assistant", "content": text})
