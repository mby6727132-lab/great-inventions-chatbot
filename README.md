# 💡 צ'אט בוט - חמשת ההמצאות הגדולות בעולם

צ'אט בוט בעברית שעונה על שאלות על חמש המצאות שינו את העולם:

- מכונת הדפוס
- נורת החשמל
- הטלפון
- המטוס
- האינטרנט

הבוט בנוי בשיטת **RAG** (Retrieval-Augmented Generation): לכל שאלה הוא מחפש את הקטעים הרלוונטיים במאגר הידע, ועונה רק על סמך המידע שנמצא בהם, בלי להמציא מידע.

## איך זה עובד

1. **הכנת המאגר** ([ingestion.py](ingestion.py)): קורא את הטקסט מתיקיית `data`, מחלק אותו לקטעים, יוצר לכל קטע embedding בעזרת `gemini-embedding-001` ושומר הכול במאגר וקטורי של ChromaDB בתיקייה `chroma_db`.
2. **מנוע החיפוש** ([rag_engine.py](rag_engine.py)): מתחבר למאגר ומחזיר את 3 הקטעים הכי קרובים לשאלה.
3. **ממשק הצ'אט** ([app.py](app.py)): אפליקציית Streamlit שרצה בדפדפן.
   - שאלת המשך (למשל "ומתי הוא נולד?") מנוסחת מחדש לשאלה עצמאית לפי היסטוריית השיחה.
   - מתבצע חיפוש של הקטעים הרלוונטיים במאגר.
   - מודל Gemini כותב תשובה בעברית על סמך הקטעים שנמצאו.
   - הבוט עונה בנימוס לברכות ולשיחת חולין, ומכוון חזרה לנושא ההמצאות כשהשאלה לא קשורה אליהן.

## מבנה הפרויקט

```
├── app.py            # ממשק הצ'אט (Streamlit)
├── rag_engine.py     # חיפוש קטעים רלוונטיים במאגר
├── ingestion.py      # בניית המאגר הווקטורי מהטקסט
├── data/
│   └── inventions.md # מאגר הידע על ההמצאות
├── chroma_db/        # המאגר הווקטורי (נוצר בהרצת ingestion.py)
├── .env              # מפתח ה-API (לא עולה ל-git)
└── README.md
```

## טכנולוגיות

- **Python**
- **Streamlit**: ממשק הצ'אט
- **LlamaIndex**: טעינת המסמכים, חלוקה לקטעים ואינדוקס
- **ChromaDB**: מאגר וקטורי
- **Google Gemini**: embeddings ויצירת תשובות (`google-genai`)

## התקנה והרצה

### 1. יצירת סביבה וירטואלית והתקנת חבילות

```bash
python -m venv venv
venv\Scripts\activate
pip install streamlit python-dotenv chromadb google-genai llama-index-core llama-index-embeddings-google-genai llama-index-vector-stores-chroma
```

### 2. הגדרת מפתח API

צרו קובץ `.env` בתיקייה הראשית של הפרויקט:

```
GEMINI_API_KEY=המפתח_שלכם
```

אפשר לקבל מפתח ב-[Google AI Studio](https://aistudio.google.com/apikey).

### 3. בניית המאגר (פעם אחת)

```bash
python ingestion.py
```

הפקודה יוצרת את תיקיית `chroma_db`. אם משנים את התוכן ב-`data`, צריך להריץ אותה שוב.

### 4. הרצת הצ'אט

```bash
streamlit run app.py
```

הדפדפן ייפתח בכתובת `http://localhost:8501`.

## דוגמאות לשאלות

- מי המציא את הדפוס?
- איך האינטרנט שינה את העולם?
- מתי טסו לראשונה במטוס?
- ומה עוד הוא המציא? (שאלת המשך)
