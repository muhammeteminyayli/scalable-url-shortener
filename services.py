import string
import threading
from typing import Tuple, Optional
from sqlmodel import Session, select
from database import Link, engine

# Define the alphabet for base62 encoding
ALPHABET = string.digits + string.ascii_lowercase + string.ascii_uppercase


def encoder(id_number: int) -> str:
    """
    Converts a numeric ID to a short code using base62 encoding.
    """
    if id_number == 0:
        return ALPHABET[0]
    
    encoded_string = ""
    base = len(ALPHABET)
    
    while id_number > 0:
        remainder = id_number % base
        encoded_string += ALPHABET[remainder]
        id_number //= base
        
    return encoded_string[::-1]


class RangeManager:
    """
    Manages ID ranges to be distributed among workers (nodes).
    This ensures that multiple workers do not generate conflicting IDs.
    """
    def __init__(self, start_id: int = 1000000, block_size: int = 1000):
        self.global_counter = start_id
        self.block_size = block_size
        self.lock = threading.Lock()

    def get_range(self) -> Tuple[int, int]:
        """
        Thread-safe method to allocate a new range of IDs.
        Returns a tuple (start, end).
        """
        with self.lock:
            start = self.global_counter
            end = start + self.block_size
            self.global_counter += self.block_size
            return start, end


class URLShortenerNode:
    """
    A worker node that generates short codes and manages database interactions.
    """
    def __init__(self, manager: RangeManager):
        self.manager = manager
        self.current_id = 0
        self.end_limit = 0

    def _get_next_id(self) -> int:
        """
        Retrieves the next available ID from the current allocated range.
        Allocates a new range if the current one is exhausted.
        """
        self.current_id += 1
        # Check if the current range is exhausted or not yet initialized
        if self.current_id == 0 or self.current_id >= self.end_limit:
            self.current_id, self.end_limit = self.manager.get_range()
        return self.current_id

    def shorten_url(self, original_url: str) -> str:
        """
        Shortens a given URL. Returns the existing short code if the URL 
        is already in the database, otherwise generates a new one.
        """
        with Session(engine) as session:
            # Check if the URL already exists
            statement = select(Link).where(Link.long_url == original_url)
            existing_link = session.exec(statement).first()

            if existing_link:
                return existing_link.short_code

            # Generate a new ID and short code
            new_id = self._get_next_id()
            short_code = encoder(new_id)
            
            # Save to database
            new_link = Link(id=new_id, long_url=original_url, short_code=short_code)
            session.add(new_link)
            session.commit()
            
            return short_code

    def get_original_url(self, short_code_or_url: str) -> Optional[str]:
        """
        Retrieves the original URL corresponding to the given short code.
        Handles both raw codes (e.g., 'abc') and full URLs (e.g., 'http://.../abc').
        """
        # Extract the code if a full URL is provided
        code = short_code_or_url.split('/')[-1]

        with Session(engine) as session:
            statement = select(Link).where(Link.short_code == code)
            result_link = session.exec(statement).first()

            if result_link:
                return result_link.long_url
            else:
                return None


# Initialize the global range manager and worker instance
range_manager = RangeManager()
worker = URLShortenerNode(range_manager)
