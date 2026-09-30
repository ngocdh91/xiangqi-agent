import ollama

# Gửi câu hỏi tới mô hình llama3
response = ollama.chat(
    model="llama3",
    messages=[
        {
            "role": "user",
            "content": "Xin chào! Bạn có thể giúp gì cho tôi?",
        },
    ],
)

# In câu trả lời
print("Mô hình trả lời:")
print(response["message"]["content"])