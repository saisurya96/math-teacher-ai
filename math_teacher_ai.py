import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import base64
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, SystemMessage

class MathTeacherAI:
    def __init__(self):
        load_dotenv()
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.store = {}
        self.setup_ai()

    def setup_ai(self):
        self.system_message = SystemMessage(
            content="""You are a kind and caring math teacher whose priority is to INTUITIVELY explain mathematical and scientific equations
            that can be difficult to understand for a normal person who finds them daunting and scary.
            Do not answer any questions that are not directly related to science or math.
            
            IMPORTANT:
            PLEASE USE LATEX TO REPRESENT MATHEMATICAL NOTATIONS OR EQUATIONS."""
        )
        
        self.chat_llm = ChatOpenAI(api_key=self.openai_api_key, model_name="gpt-4o", temperature=0)
        
        self.prompt = ChatPromptTemplate.from_messages([
            self.system_message,
            MessagesPlaceholder(variable_name="image"),
            MessagesPlaceholder(variable_name="history"),
            MessagesPlaceholder(variable_name="human_input"),
        ])
        
        self.chain = self.prompt | self.chat_llm
        self.with_message_history = RunnableWithMessageHistory(
            self.chain,
            lambda session_id: self.get_session_history(session_id),
            input_messages_key="human_input",
            history_messages_key="history",
        )

    def get_session_history(self, session_id: str):
        if session_id not in self.store:
            self.store[session_id] = InMemoryChatMessageHistory()
        return self.store[session_id]

    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
        

    def process_query(self, query, session_id, image_path=None):
        config = {"configurable": {"session_id": session_id}}
        
        image_message = None
        if image_path:
            img_dc = self.encode_image(image_path)
            image_message = HumanMessage(
                content=[
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{img_dc}"},
                    },
                ]
            )

        response = self.with_message_history.invoke(
            {
                "image": [image_message] if image_message else [],
                "human_input": [HumanMessage(content=query)]
            },
            config=config,
        )
        return response.content.replace(r'\(', '$').replace(r'\)', '$').replace(r'\[', '$').replace(r'\]', '$')

# Example usage
# if __name__ == "__main__":
#     math_ai = MathTeacherAI()
    
    # Example with an image
    # response = math_ai.process_query("What's this equation about?", "session1", "eq.png")
    # print("Response with image:", response)
    
    # Example without an image
    # response = math_ai.process_query("Can you explain the Pythagorean theorem?", "session1")
    # print("Response without image:", response)