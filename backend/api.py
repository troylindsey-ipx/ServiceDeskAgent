from livekit.agents import llm
import enum
import logging
import re
from db_ticket import DatabaseTicket

logger = logging.getLogger("user-data")
logger.setLevel(logging.INFO)

DB = DatabaseTicket()

# Phonetic alphabet mapping
PHONETIC_ALPHABET = {
    'alpha': 'A', 'bravo': 'B', 'charlie': 'C', 'delta': 'D', 'echo': 'E', 
    'foxtrot': 'F', 'golf': 'G', 'hotel': 'H', 'india': 'I', 'juliet': 'J',
    'kilo': 'K', 'lima': 'L', 'mike': 'M', 'november': 'N', 'oscar': 'O',
    'papa': 'P', 'quebec': 'Q', 'romeo': 'R', 'sierra': 'S', 'tango': 'T',
    'uniform': 'U', 'victor': 'V', 'whiskey': 'W', 'xray': 'X', 'x-ray': 'X',
    'yankee': 'Y', 'zulu': 'Z'
}

def convert_phonetic_to_letters(text: str) -> str:
    """Convert phonetic alphabet words to their corresponding letters"""
    if not text:
        return text
    
    # Split by common separators (dash, space, etc.)
    parts = re.split(r'[-\s]+', text.lower())
    result_parts = []
    
    for part in parts:
        # Check if this part is a phonetic alphabet word
        if part in PHONETIC_ALPHABET:
            result_parts.append(PHONETIC_ALPHABET[part])
        else:
            # Keep non-phonetic parts as-is (like numbers)
            result_parts.append(part.upper())
    
    return ''.join(result_parts)

def format_ticket_number_for_speech(ticket_number: str) -> str:
    """Format ticket number for clear speech pronunciation, especially zeros"""
    if not ticket_number:
        return ticket_number
    
    # Replace zeros with "zero" to ensure clear pronunciation
    # Split into letters and numbers for better pronunciation
    formatted = ""
    for char in ticket_number:
        if char == '0':
            formatted += "zero "
        elif char.isdigit():
            formatted += char + " "
        else:
            formatted += char
    
    return formatted.strip()

class TicketDetails(enum.Enum):
    Inc = "inc"
    First = "first"
    Last = "last"
    Comp_Name = "comp_name"
    Bldg = "bldg"
    Issue = "issue"
    

class AssistantFnc:
    def __init__(self, participant_name: str = ""):
        self._participant_name = participant_name
        self._parsed_name = self._parse_participant_name(participant_name)
        
        self._ticket_details = {
            TicketDetails.Inc: "",
            TicketDetails.First: self._parsed_name.get("first", ""),
            TicketDetails.Last: self._parsed_name.get("last", ""),
            TicketDetails.Comp_Name: "",
            TicketDetails.Bldg: "",
            TicketDetails.Issue: ""
        }
    
    def _parse_participant_name(self, name: str) -> dict:
        """Parse participant name into first and last name"""
        if not name or name.lower() in ["anonymous", "there"]:
            return {"first": "", "last": ""}
        
        # Split name by space and assume first word is first name, rest is last name
        parts = name.strip().split()
        if len(parts) == 1:
            return {"first": parts[0], "last": ""}
        elif len(parts) >= 2:
            return {"first": parts[0], "last": " ".join(parts[1:])}
        else:
            return {"first": "", "last": ""}
    
    def get_ticket_str(self):
        ticket_str = ""
        for key, value in self._ticket_details.items():
            # Format incident number for clear speech pronunciation
            if key == TicketDetails.Inc and value:
                formatted_value = format_ticket_number_for_speech(value)
                ticket_str += f"{key.value}: {formatted_value}\n"
            else:
                ticket_str += f"{key.value}: {value}\n"
            
        return ticket_str
    
    @llm.function_tool(description="lookup a ticket by its incident number")
    async def lookup_ticket(self, inc: str):
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
    
    @llm.function_tool(description="search for tickets by user's first and last name")
    async def search_tickets_by_name(self, first_name: str, last_name: str = ""):
        logger.info("search tickets by name - first: %s, last: %s", first_name, last_name)
        
        try:
            # Try to find tickets by name (this would need to be implemented in the database)
            # For now, we'll return a message indicating we searched
            return f"Searched for tickets for {first_name} {last_name}. If you have an existing incident number, please provide it. Otherwise, I'll help you create a new ticket."
        except Exception as e:
            logger.error("Error searching tickets by name: %s", str(e))
            return "Unable to search for existing tickets at this time. I'll help you create a new ticket."
    
    @llm.function_tool(description="get the details of the current ticket")
    async def get_ticket_details(self):
        logger.info("get ticket details")
        return f"The ticket details are: {self.get_ticket_str()}"
    
    @llm.function_tool(description="create a new ticket with user information and issue description")
    async def create_ticket(
        self, 
        first: str,
        last: str,
        comp_name: str,
        bldg: str,
        issue: str
    ):
        # Use participant's name if AI provides placeholder text or empty values
        actual_first = first
        actual_last = last
        
        # Check for placeholder text or empty values and use participant name instead
        if (not first or first.lower() in ["user's first name", "first name", "user", "customer"] or
            not last or last.lower() in ["user's last name", "last name", "surname"]):
            actual_first = self._parsed_name.get("first", first)
            actual_last = self._parsed_name.get("last", last)
            logger.info("Using participant name instead of placeholder - original: %s %s, using: %s %s", 
                       first, last, actual_first, actual_last)
        
        # Convert phonetic alphabet in computer name to letters
        converted_comp_name = convert_phonetic_to_letters(comp_name)
        logger.info("create ticket - first: %s, last: %s, comp_name: %s (converted from: %s), bldg: %s, issue: %s", 
                   actual_first, actual_last, converted_comp_name, comp_name, bldg, issue)
        
        try:
            # Pass empty string for inc since it will be auto-generated
            result = DB.create_ticket("", actual_first, actual_last, converted_comp_name, bldg, issue)
            if result is None:
                logger.error("Database returned None when creating ticket")
                return "Failed to create ticket"
            
            logger.info("Ticket created successfully with INC: %s", result.inc)
            
            self._ticket_details = {
                TicketDetails.Inc: result.inc,
                TicketDetails.First: result.first,
                TicketDetails.Last: result.last,
                TicketDetails.Comp_Name: result.comp_name,
                TicketDetails.Bldg: result.bldg,
                TicketDetails.Issue: result.issue
            }
            
            # Format ticket number for clear speech pronunciation
            formatted_inc = format_ticket_number_for_speech(result.inc)
            return f"Ticket created successfully! Your incident number is {formatted_inc}. The ticket has been submitted and you will receive updates on the status."
            
        except Exception as e:
            logger.error("Error creating ticket: %s", str(e))
            return f"Failed to create ticket due to error: {str(e)}"
    
    def has_ticket(self):
        return self._ticket_details[TicketDetails.Inc] != ""
