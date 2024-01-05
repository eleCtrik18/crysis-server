from src.repositories.wallet import WalletRepository
from src.schema.common import APIResponse


class WalletService:
    def __init__(self, db, user_obj):
        self.db = db
        self.user_id = user_obj.id

    def create_wallet(
        self,
    ):
        try:
            wallet = WalletRepository(self.db).create_user_wallet(self.user.id)
            return APIResponse(success=True, message="User Wallet created")
        except Exception as e:
            return APIResponse(
                success=False, message="Something Went Wrong", error=str(e)
            )

    def get_wallet(
        self,
    ):
        try:
            wallet = WalletRepository(self.db).get_user_wallet(self.user_id)
            return APIResponse(
                success=True, message="Wallet Details fetch", data={"wallet": wallet}
            )
        except Exception as e:
            return APIResponse(success=False, message="No details found", error=str(e))
