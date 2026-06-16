from database.repositories.contract_repository import ContractRepository

class ContractService:

    @staticmethod
    def register(contract):

        if ContractRepository.exists(
            contract["contract_id"]
        ):
            return

        ContractRepository.save(contract)