import os
import google.generativeai as genai
from dotenv import load_dotenv
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# تحميل متغيرات البيئة من ملف .env
load_dotenv()

# إعداد Gemini API
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
except Exception as e:
    print(f"Error configuring Gemini API: {e}")
    model = None

class GeminiChatView(APIView):
    def post(self, request, *args, **kwargs):
        if not model:
            return Response(
                {"error": "Gemini API not configured correctly."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # الحصول على السؤال من طلب POST
        prompt = request.data.get('prompt')

        if not prompt:
            return Response(
                {"error": "Prompt is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # إرسال السؤال إلى Gemini والحصول على الإجابة
            response = model.generate_content(prompt)
            
            # إرجاع الإجابة كـ JSON
            return Response({"response": response.text}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": f"An error occurred with the Gemini API: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )