from pydantic import BaseModel


class BaseMessage(BaseModel):
    def __str__(self):
        return f"{self.__class__.__name__}({super().__str__()})"
