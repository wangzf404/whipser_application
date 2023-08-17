import openai
import logging
# 设置日志级别为ERROR
logging.basicConfig(level=logging.ERROR)

openai_key = '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'
target_language = 'zh-hans'


def summarize_text(input_text, max_tokens=300):
    openai.api_key = openai_key
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"请总结以下文本,要求条理清晰,数字序号列出概要,并且强制要求长度不超过{max_tokens}个tokens:"},
                {"role": "user", "content": f"文本内容:`{input_text}`. Target language: zh-hans"}
            ]
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        logging.exception("Failed")