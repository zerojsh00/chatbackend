from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import StreamingHttpResponse
from .rag import RAG
from time import sleep

import my_settings
import openai
import json
import os

@method_decorator(csrf_exempt, name='dispatch')
class ChatView(View):
    def post(self, request):
        openai.api_key = my_settings.API_KEY
        os.environ["OPENAI_API_KEY"] = my_settings.API_KEY

        # Parse the request body and extract the prompt
        query = json.loads(request.body)['content']

        try:
            generated_sentence = RAG(query=query).get_sentence()

            # Define a generator function to stream the response
            def generate_response():
                prompt = "translate following sentence in Korean {}".format(generated_sentence)
                for chunk in openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{
                            "role": "user",
                            "content": prompt
                        }],
                        stream=True,
                ):

                    content = chunk["choices"][0].get("delta", {}).get("content")
                    if content is not None:
                        yield content

    #        Return a streaming response to the client
            return StreamingHttpResponse(generate_response(), content_type="application/octet-stream")

        except Exception :
            def generate_err_msg():
                err_msg = "죄송합니다. 아직 지원하지 않는 유형의 질문입니다."
                for tok in err_msg:
                    sleep(0.02) # 스트리밍의 효과를 주기 위해 ...
                    yield tok

            return StreamingHttpResponse(generate_err_msg(), content_type="application/octet-stream")


        # Return a JSON error if the request method is not POST
        return JsonResponse({'error': 'Method not allowed.'}, status=405)

