from src.repositories.prices import Gold24PriceRepository
from src.repositories.wallet import WalletRepository
from src.schema.common import APIResponse
from src.utils.mathutils import truncate_to_2_decimal


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
        
    def convert_gold_to_amount(self):
        try:

            current_gold_price = Gold24PriceRepository(self.db).get_latest_price()
            # print(current_gold_price)

            wallet_details = WalletRepository(self.db).get_user_wallet(self.user_id)
            quantity_value = wallet_details['quantity']

            current_aura_sell_price = current_gold_price.aura_sell_price

            # print(current_aura_sell_price)

            amount = quantity_value * current_aura_sell_price
            final_amount = truncate_to_2_decimal(amount)

            return APIResponse(
                success=True,
                message="Conversion successful",
                data={"amount": final_amount, "gold_quantity":  quantity_value},
            )
        except Exception as e:
            return APIResponse(
                success=False,
                message="Conversion failed",
                error=str(e)
            )
        
    def get_wallet_with_conversion(self):
        try:
            # Get wallet details
            wallet_details_response = self.get_wallet()

            # Check if getting wallet details was successful
            if wallet_details_response.success:
                conversion_response = self.convert_gold_to_amount()

                # Check if conversion was successful
                if conversion_response.success:
    
                    combined_data = {
                        "wallet_details": conversion_response.data,
                    }

                    return APIResponse(
                        success=True,
                        message="Combined response",
                        data=combined_data,
                    )
                else:
                    return conversion_response 
            else:
                return wallet_details_response 
        except Exception as e:
            return APIResponse(
                success=False,
                message="Something Went Wrong",
                error=str(e),
            )    