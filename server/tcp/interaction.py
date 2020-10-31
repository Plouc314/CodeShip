from spec import Spec

class Interaction:
    '''
    Static object.  

    Manage the interaction between the clients.
    '''

    clients = []

    @classmethod
    def send_general_chat_msg(cls, username, msg):
        '''
        Send a message to all connected clients on the general chat.
        '''

        for client in cls.clients:

            if client.username == username:
                continue
        
            # send message
            msg = f'gc{Spec.SEP_MAIN}{username}{Spec.SEP_CONTENT}{msg}'
            client.send(msg)
