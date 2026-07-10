import os
from groq import Groq
def ask_groq(prompt: str) -> str:
    client = Groq( api_key = os.environ.get("GROQ_API_KEY"),)
    response = client.chat.completions.create(messages = [       #client - chat related -completion(response to a conversation) - create it 
        {
          "role" : "user" ,
          "content" : prompt  
        }
    ],
    model = "llama-3.3-70b-versatile"
    )
    return response.choices[0].message.content                #reponses - stored inside choices - among that first one [0 index] -its message - inside its content

if __name__ == "__main__":
    print(ask_groq("What is the capital of France?"))
    