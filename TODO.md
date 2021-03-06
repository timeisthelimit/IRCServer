# TODO?

## Channels
- Channel Opertaor
    - Identified with '@' symbol next to their nickname when it is associated wiht a channel (i.e. replying to NAMES, WHO, WHOIS)

## Messages
- Character Codes
    - No specific char set specified
    - Protocol is based on a set of 8-bit codes (octets)
    - A message is made up of any number of these octets
    - Some octet values act as message delimiters
    - Curly braces '{}' are lowercase equivelent of square brackets '[]'
- Messages
    - Not all messages generate a reply
    - A valid command from a client is expected to generate a reply from the server
    - It is not advised to wait forever for a reply
    - A message consists of:
        - prefix (optional)
            - presence of a prefix is indicated with a single leading colon (0x3a)
                - the colon must be the first character of the message
                - there must be not gap between the colon and the prefix
            - used by servers to indicated the true origin of the message
            - no prefix indicates that the true origin is the connection on which the message was received
            - Clients should not use a prefix, the only valid prefix for them to use is their nickname
            - if the source of the message cannot be identified in the servers internal database, the server must silently ignore the message
        - command
            - valid IRC command or a three digit number represented in ASCII text
        - command parameters (up to 15)
        - all constituents are separated by one or more ASCII space (0x20)
        - messages are always terminated with CR-LF pair
        - messages shall not exceed 512 characters
            - including CR-LF so max 510 for the rest of the message
    - See RFC 1459 for message structure in psudo BNF

## Registration
- check values passed comply with documentation
    - if not throw ValueError with a descriptive message (e.g. invalid nick)
- check whether nick exists in nick dictionary in server class object
    - throw appropriate error

## Message Details
- for each message
    - check that all necessary parameters are present
    - check each parameter for validity
    - send appropriate respone to the client
    - in the case of a comma separated list parameter a rely must be sent for each item in the list

- ~~QUIT~~ [Quit Message]
    - ~~upon receiving this message from a client the server must close the connection with that client~~
