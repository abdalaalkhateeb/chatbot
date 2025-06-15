import os
import google.generativeai as genai
from dotenv import load_dotenv
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
import mimetypes
from pathlib import Path

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
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        if not model:
            return Response(
                {"error": "Gemini API not configured correctly."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # الحصول على السؤال وملف PDF من طلب POST
        prompt = request.data.get('prompt')
        file_obj = request.FILES.get('file')

        if not prompt:
            return Response(
                {"error": "Prompt is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            if file_obj:
                # التحقق من أن الملف PDF
                if not file_obj.name.lower().endswith('.pdf'):
                    return Response(
                        {"error": "Only PDF files are supported."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # حفظ الملف مؤقتاً
                temp_file_path = os.path.join('temp', file_obj.name)
                os.makedirs('temp', exist_ok=True)
                
                with open(temp_file_path, 'wb+') as destination:
                    for chunk in file_obj.chunks():
                        destination.write(chunk)
                
                try:
                    # إرسال الملف مع السؤال إلى Gemini
                    response = model.generate_content([prompt, temp_file_path])
                finally:
                    # حذف الملف المؤقت بعد الاستخدام
                    if os.path.exists(temp_file_path):
                        os.remove(temp_file_path)
            else:
                # إرسال السؤال فقط إذا لم يتم تحميل ملف
                response = model.generate_content(prompt)
            
            # إرجاع الإجابة كـ JSON
            return Response({"response": response.text}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )