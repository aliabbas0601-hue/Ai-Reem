import streamlit as st
from google import genai
from google.genai import types

# إعدادات الصفحة
st.set_page_config(
    page_title="مساعدتي ريم 🇸🇾",
    page_icon="👧",
    layout="centered"
)

# دعم التنسيق من اليمين لليسار للغة العربية وتجميل الواجهة
st.markdown("""
    <style>
    .stApp {
        direction: rtl;
        text-align: right;
        background-color: #f7f9fc;
    }
    .stChatMessage {
        direction: rtl;
        text-align: right;
        border-radius: 12px;
        padding: 10px;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background-color: #4A90E2;
        color: white;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.title("👧 المحادثة مع ريم")
st.caption("صبيّة سورية عمرها 20 سنة - جاهزة لترغى وتحكي معك!")

# تعليمات شخصية ريم (System Prompt)
SYRIAN_REEM_PROMPT = """
أنتِ فتاة اسمُكِ "ريم"، عمرُكِ 20 سنة، وجنسيتُكِ سورية.
طبيعة شخصيتك:
- تتحدثين دائماً وبالكامل باللهجة السورية المحكية العفوية واللطيفة (مثل: "كيفك"، "شو في ما في"، "يا عيني"، "تقبرني"، "لك أهلين"، "تأبر قلبي").
- شخصيتك مرحة، خفيفة الدم، عفوية، وذكية بنفس الوقت.
- تجيبين بطريقة طبيعية وكأنك صديقة مقربة تتحدث في دردشة عادية وليست روبوت أو ذكاء اصطناعي.
- لا تخرجين عن هذه الشخصية أبداً تحت أي ظرف، ولا تتحدثين باللغة العربية الفصحى الجافة إلا إذا طُلب منك ترجمة شيء معين.
"""

# الشريط الجانبي للإعدادات
with st.sidebar:
    st.header("⚙️ الإعدادات")
    api_key = st.text_input("أدخل مفتاح Gemini API:", type="password", help="احصل على مفتاح مجاني من Google AI Studio")
    
    if st.button("بدء محادثة جديدة 🗑️"):
        st.session_state.messages = []
        st.rerun()

# تهيئة سجل المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض الرسائل السابقة
for message in st.session_state.messages:
    avatar = "👧" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# منطقة استقبال مدخلات المستخدم
if prompt := st.chat_input("احكي مع ريم..."):
    if not api_key:
        st.error("حط مفتاح الـ API بالشريط الجانبي أولاً لتدردش مع ريم!")
    else:
        # عرض رسالة المستخدم
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        # توليد رد ريم
        with st.chat_message("assistant", avatar="👧"):
            try:
                client = genai.Client(api_key=api_key)
                
                # تحويل سجل المحادثة لصيغة API
                contents = []
                for msg in st.session_state.messages:
                    role = "user" if msg["role"] == "user" else "model"
                    contents.append(types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])]))

                # استدعاء النموذج مع تثبيت شخصية ريم
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=SYRIAN_REEM_PROMPT,
                        temperature=0.8,
                    )
                )
                
                response_text = response.text
                st.markdown(response_text)
                
                # إضافة الخاصية الصوتية لتحويل النص إلى صوت ريم
                tts_script = f"""
                <script>
                    var msg = new SpeechSynthesisUtterance("{response_text.replace('"', '').replace('\n', ' ')}");
                    msg.lang = 'ar-SY';
                    window.speechSynthesis.speak(msg);
                </script>
                """
                st.components.v1.html(tts_script, height=0)

                # حفظ رد ريم في السجل
                st.session_state.messages.append({"role": "assistant", "content": response_text})

            except Exception as e:
                st.error(f"صار مشكلة بالاتصال: {str(e)}")
