from livekit.agents import llm
import enum
from typing import Annotated
import logging
from ServiceDeskAgent.backend.db_ticket import DatabaseTicket

logger = logging.getLogger("user-data")
logger.setLevel(logging.INFO)

DB = DatabaseTicket()

class TicketDetails(enum.Enum):
    Inc = "inc"
    First = "first"
    Last = "last"
    Comp_Name = "comp_name"
    Bldg = "bldg"
    Issue = "issue"
    

class AssistantFnc(llm.FunctionContext):
    def __init__(self):
        super().__init__()
        
        self._ticket_details = {
            TicketDetails.Inc: "",
            TicketDetails.First: "",
            TicketDetails.Last: "",
            TicketDetails.Comp_Name: "",
            TicketDetails.Bldg: "",
            TicketDetails.Issue: ""
        }
    
    def get_ticket_str(self):
        ticket_str = ""
        for key, value in self._ticket_details.items():
            ticket_str += f"{key}: {value}\n"
            
        return ticket_str
    
    @llm.ai_callable(description="lookup a ticket by its incident nubmer")
    def lookup_ticket(self, inc: Annotated[str, llm.TypeInfo(description="The inc of the ticket to lookup")]):
        logger.info("lookup ticket - inc: %s", inc)
        
        result = DB.get_ticket_by_inc(inc)
        if result is None:
            return "Ticket not found"
        
        self._ticket_details = {
            TicketDetails.Inc: result.inc,
            TicketDetails.First: result.first,
            TicketDetails.Last: result.last,
            TicketDetails.Comp_Name: result.comp_name,
            TicketDetails.Bldg: result.bldg,
            TicketDetails.Issue: result.issue
        }
        
        return f"The ticket details are: {self.get_ticket_str()}"
    
    @llm.ai_callable(description="get the details of the current ticket")
    def get_ticket_details(self):
        logger.info("get ticket details")
        return f"The ticket details are: {self.get_ticket_str()}"
    
    @llm.ai_callable(description="create a new ticket")
    def create_ticket(
        self, 
        inc: Annotated[str, llm.TypeInfo(description="The inc of the ticket")],
        first: Annotated[str, llm.TypeInfo(description="The first name on the ticket ")],
        last: Annotated[str, llm.TypeInfo(description="The last name on the ticket")],
        comp_name: Annotated[str, llm.TypeInfo(description="The computer name on the ticket")],
        bldg: Annotated[str, llm.TypeInfo(description="The building the user works in")],
        issue: Annotated[str, llm.TypeInfo(description="The issue the user is facing")]
    ):
        logger.info("create ticket - inc: %s, first: %s, last: %s, comp_name: %s, bldg: %s, issue: %s", inc, first, last, comp_name, bldg, issue)
        result = DB.create_ticket(inc, first, last, comp_name, bldg, issue)
        if result is None:
            return "Failed to create ticket"
        
        self._ticket_details = {
            TicketDetails.Inc: result.inc,
            TicketDetails.First: result.first,
            TicketDetails.Last: result.last,
            TicketDetails.Comp_Name: result.comp_name,
            TicketDetails.Bldg: result.bldg,
            TicketDetails.Issue: result.issue
        }
        
        return "ticket created!"
    
    def has_ticket(self):
        return self._ticket_details[TicketDetails.Inc] != ""