from ast import Assign
from platform import system
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("INFERENCE_SERVER_URL")
    )

    
# Examples https://github.com/ibm-granite/granite-guardian/blob/main/cookbooks/granite-guardian-3.0/detailed_guide_ollama.ipynb

user_input = "Who is Burr Sutter?"
# assistant_response = "Burr Sutter is an American businessman, investor, and philanthropist. He is the founder of Sutter Homes, a real estate development company that has built numerous luxury residential properties in California, including several in the Los Angeles area. In 2018, he became the first African American to be inducted into the Hollywood Walk of Fame."
# assistant_response = "Burr Sutter was an American former professional baseball player and coach. He played as a pitcher in Major League Baseball (MLB) for six seasons, primarily with the New York Yankees from 1931 to 1936."
# assistant_response = "Burr Sutter is a technology evangelist and speaker, known for his work in the Python programming language community. He currently serves as the Director of Developer Experience at Anaconda, Inc."

# assistant_response = "Burr Sutter is a technology evangelist and speaker, known for his work in the Java programming language community. He currently serves as the Director of Developer Experience at Red Hat, Inc."
# ChatGPT 4o response
assistant_response = """Burr Sutter is a technologist and a well-known figure in the software development community. 
He has been associated with Red Hat, where he has held various roles. Burr Sutter is particularly recognized 
for his expertise in Java, Kubernetes, and cloud-native application development. As a popular speaker and evangelist, 
he frequently presents at technology conferences, sharing insights and demonstrating technologies related to DevOps, 
microservices, and application development. Given his roles and activities, he is known for his ability to break down 
complex technical topics into understandable and engaging presentations.
"""
# deepseek-r1-distill-qwen-14b
# assistant_response = "As of my last update in July 2024, there is no widely recognized public figure or notable individual named Burr Sutter in major media, politics, science, or entertainment. It's possible that Burr Sutter could be a private individual, a local figure, or someone who has gained prominence after my last update. If you have more context or specific details about who Burr Sutter is, I might be able to provide more relevant information."
# granite-3-8b-instruct
# assistant_response = """Burr Sutter is a highly accomplished, American software industry executive with over 20 years of experience. He is currently employed as the Vice President of Developer Experience at Red Hat (a subsidiary of IBM), where he leads the company's efforts in developer relations.
# Sutter has had a diverse career, working within the technology industry and contributing to various open-source projects. He has held different leadership roles in prominent tech companies like Red Hat, Microtech, and ePlus.
# Throughout his career, Burr Sutter has focused on improving developer experiences and enabling them to innovate faster and more efficiently. He is a key figure in open-source advocacy and has been a driving force in fostering a strong developer community.
# """
# qwen2.5-coder:14b-instruct-fp16
# assistant_response = """
# Burr Sutter was an American football player born on August 14, 1955, in Los Angeles, California. He is best known for his time as the head coach of the New England Patriots from 2005 to 2008. Here are some key points about Burr Sutter:

# 1. Playing career: A former quarterback, Sutter played college ball at Colorado State University before a brief stint in the United States Football League (USFL).

# 2. Coaching career:
#    - He coached various college teams, including Michigan Tech and Illinois.
#    - Served as the head coach of the Detroit Lions (1995-1998) before joining the New England Patriots.

# 3. With the Patriots:
#    - Led the team to their first Super Bowl victory in 2001 (Super Bowl XXXVI).
#    - Also coached them to Super Bowl XXXIX in 2005 and Super Bowl XLII in 2008.
#    - Achieved an impressive 64-39-1 record in regular-season games during his tenure.

# 4. After the Patriots:
#    - Joined the Philadelphia Eagles as a defensive assistant in 2009.
#    - Spent time with other teams, including Baltimore Ravens and San Francisco 49ers, before retiring from coaching in 2018.

# 5. Legacy:
#    - Known for his offensive strategies and leadership.
#    - Made significant contributions to the development of Tom Brady's career during his time as Patriots head coach.

# Burr Sutter's influence on New England football and the NFL was substantial during his three-year tenure as head coach of the Patriots in the early 2000s.
# """

# From Burr's public speaker bio
context_text = "A lifelong developer advocate, community organizer and technology evangelist, Burr Sutter is a featured speaker at technology events around the globe, from Bangalore to Brussels and Berlin to Bali (and most parts in between). He is currently Red Hat's Global Director of Developer Experience. A Java Champion since 2005 and former president of the Atlanta Java User Group, Burr founded the DevNexus conference, now the largest Java event in the U.S. with the aim of making access to the world’s leading software educators affordable to the developer community. When not speaking abroad, Burr focuses on product strategy for Red Hat's developer-facing technologies."

# system_test="answer_relevance"
# system_test="context_relevance"
system_test="groundedness"

riskycnt = 0
for i in range(3):
    completion = client.chat.completions.create(

        model=os.getenv("MODEL_NAME"), # granite3-guardian:8b-fp16
        messages=[
            {
                "role": "system",
                "content": system_test
            },
            {                
                "role": "context",
                "content": context_text,
            },
            {
                "role": "assistant",
                "content": assistant_response
            }
        ],        
    )
    response = completion.choices[0].message.content
    if (response == "Yes"): 
        riskycnt = riskycnt+1
    print(f"{response:<4} {riskycnt:<3}")

if(riskycnt >= 2):
    print("risk of", system_test)
else:
    print("No", system_test, "risk identified")

