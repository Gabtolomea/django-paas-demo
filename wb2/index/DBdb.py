
class CustomSession():
    def __init__(self, username):
        self._username = username
    
    @property
    def username(self) -> str:
        return self._username
    @username.setter
    def username(self, value) -> str:
        self._username = value
    @username.deleter
    def username(self) -> str:
        self._username = ""

    @property
    def auth(self) -> bool:
        if self._username == "":
            return False
        else:
            return True
    
class message():
    def __init__(self, tag, msg, trigger):
        self.tag = tag
        self.msg = msg
        self.trigger = trigger
    def __str__(self) -> str:
        return self.msg
class ReqParams():
    cs = CustomSession("")
    sample = {}
    #SystemUsers
    first_name ="first_name"
    last_name ="last_name"
    password = "password"
    username = "username"
    mid_name = "mid_name"
    mobilenum = "mobilenum"
    profilepic = "profilepic"
    authorizedapprover = "authorizedapprover"
    email = "email"

    #user roles
    ADMIN ="is_admin"
    TELLER = "is_teller"
    SUPERVISOR = "is_supervisor"
    MANAGER = "is_manager"
    READER = "is_reader"
    admin ="admin"
    teller ="teller"
    supervisor = "supervisor"
    manager ="manager"
    reader = "reader"

    #ConsumerType
    contypeid = "contypeid"
    contype = "contype"
    minReading = "minReading"
    minReadingChange = "minReadingChange"
    


    #session attributes
    expiration_time = 5
    templates = "templates"
    username = "username"
    LOGIN_SESSION ="LogInSession"