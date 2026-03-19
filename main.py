from db import migrate
from app import TerraGaugeApp

migrate()
if __name__ == "__main__":
    TerraGaugeApp().run()