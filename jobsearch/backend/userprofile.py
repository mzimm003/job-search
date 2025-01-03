
class UserProfile:
    def __init__(
            self,
            user:str
            ) -> None:
        self.user = user
    
    @classmethod
    def by_existing_user(
        cls,
        username:str
        ):
        ret = cls(user=username)

    @classmethod
    def by_creating_user(
        cls,
        username:str):
