from src.schema.common import APIResponse
import json
import os


class Dashboard:
    def __init__(self) -> None:
        self.dir = os.getcwd() + "/src/contracts/dashboard_contracts.json"
        self.file = open(self.dir)
        self.data = json.load(self.file)

    def get_layout(self):
        if self.data:
            return APIResponse(success=True, data=self.data)
        else:
            return APIResponse(
                success=False, message="Something went wrong try again later"
            )
