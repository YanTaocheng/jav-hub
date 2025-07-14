from typing import Optional, Union
from pydantic import BaseModel, Field


class JavActor(BaseModel):
    # javdb上的id
    id: str
    # javdb上的演员名
    name: str
    # javdb上的所有曾用演员名
    names: Union[str, list]
    # 自定义名称
    custom_name: Optional[str] = ""
    # 头像链接
    avatar: Optional[str] = ""
    # 演员类型
    type: Optional[str] = ""

    
