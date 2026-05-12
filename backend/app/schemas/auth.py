from pydantic import BaseModel, ConfigDict, Field


class UserProfileBase(BaseModel):
    real_name: str | None = Field(default=None, max_length=50)
    email: str | None = Field(default=None, max_length=120)
    school: str | None = Field(default=None, max_length=120)
    major: str | None = Field(default=None, max_length=120)
    grade: str | None = Field(default=None, max_length=50)
    student_no: str | None = Field(default=None, max_length=50)
    class_name: str | None = Field(default=None, max_length=80)
    gender: str | None = Field(default=None, max_length=20)
    age: str | None = Field(default=None, max_length=10)
    bio: str | None = Field(default=None, max_length=500)


class UserCreateRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=4, max_length=50)
    role: str = Field(default="student")
    class_id: int | None = None
    profile: UserProfileBase | None = None


class UserProfileUpdateRequest(UserProfileBase):
    pass


class LoginRequest(BaseModel):
    username: str
    password: str


class UserProfileResponse(UserProfileBase):
    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    class_id: int | None = None
    profile: UserProfileResponse | None = None

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse
