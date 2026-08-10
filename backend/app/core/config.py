from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "mysql+pymysql://household:household@localhost:3306/household_budget"
    cors_origins: list[str] = ["http://localhost:3000"]


settings = Settings()
