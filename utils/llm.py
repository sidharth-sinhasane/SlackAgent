import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from schema.tickit_details_schema import TicketDetailsSchema
from langchain_openai import OpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from dotenv import load_dotenv

load_dotenv()

def get_ticket_details(metadata: dict) -> TicketDetailsSchema:

    parser = PydanticOutputParser(pydantic_object=TicketDetailsSchema)

    #print(parser.get_format_instructions())

    print("@"*100)
    print(metadata['existing_tickets'], metadata['messages'], metadata['query'])
    print("@"*100)

    prompt = PromptTemplate(
        template="""
        You are an expert legal assistant. You will be provided with a list of messages and a list of existing tickets and a user request.
        You need to generate a ticket details schema.

        context: 
        - you are creating a tickets from the messages of slack channel.
        - your ticket is going to be created in jira. so try to sound like jira ticket.

        Rules:
        - if you think this discussion is not related to jira, then you should not create a ticket.insted make should_create_ticket as false. and other fields as empty.
        - if you think this discussion is related to jira, then you should create a ticket. and make should_create_ticket as true. and give the details like description, title, priority, assignee,.....
        - if the topic of discussion have the ticket already then you should not create a ticket. instead make should_create_ticket as false. and other fields as empty.

        Messages: {messages}
        Existing tickets: {existing_tickets}
        User request: {query}
        Output: {format_instructions}
        """,
        input_variables=["messages", "existing_tickets", "query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
        output_parser=parser
    )

    model = OpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))

    # Chain for better structure: prompt -> model -> parser
    chain = prompt | model | parser
    result = chain.invoke({"messages": metadata['messages'], "existing_tickets": metadata['existing_tickets'], "query": metadata['query']})

    #print(result)
    return result.dict()

if __name__ == "__main__":
    metadata = {
        'messages': [
            'Hello, how are you?',
            'I need help with my ticket',
            'we need to create a ticket for building websocket connection with the slack server this is the high priority ticket',
        ],
        'existing_tickets': [],
        'query': 'create a ticket for building websocket connection with the slack server'
    }
    get_ticket_details(metadata)