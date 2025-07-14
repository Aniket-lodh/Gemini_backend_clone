from enum import Enum
import secrets
import uuid


class TokenType(Enum):
    URL_SAFE = "url_safe"
    HEX = "hex"
    UUID = "uuid"


class Security:

    @staticmethod
    def generate_unique_id(length: int = 16, type: TokenType = TokenType.HEX) -> str:
        """Generate unique identifier based on specified type.

        Args:
            length: Length of token (for hex/urlsafe). Defaults to 16.
            type: Type of token to generate. Defaults to HEX.

        Note:
            In terms of UUID token type length is always 16

        Returns:
            str: Generated unique identifier

        Raises:
            ValueError: If invalid token type specified
        """
        if type == TokenType.URL_SAFE:
            return secrets.token_urlsafe(length)
        elif type == TokenType.HEX:
            return secrets.token_hex(length)
        elif type == TokenType.UUID:
            return str(uuid.uuid4())
        else:
            raise ValueError(f"Invalid token type: {type}")
