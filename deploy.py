from solcx import install_solc, compile_standard
import json
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()
_solc_version = "0.6.0"
install_solc(_solc_version)

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

    # Compile our solidity
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version=_solc_version,
)

# print(compiled_sol)

with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

# get bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

# get abi

abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]
# print(abi)

# connecting to kavan
w3 = Web3(
    Web3.HTTPProvider("https://kovan.infura.io/v3/c6288bd244be44d4ae10b6718b9330dc")
)
chain_id = 42

my_address = "0x64013F8A2932F0c8544993B831F2dfD48a9bA865"
# Add private key with the 0x prefix and then the private key
# private_key = "0xd28f3140427571332305fdcd94d086e7440986338c382ae9137fdf5c29526c06"

private_key = os.getenv("PRIVATE_KEY")
# print(private_key)

SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)
# print(SimpleStorage)

# 1 : Build the contract deploy transaction
# 2 : Sigh the Transaction
# 3 : Send the transaction
# Get the latestst transaction
nonce = w3.eth.getTransactionCount(my_address)
# print(nonce)

# 1
transaction = SimpleStorage.constructor().buildTransaction(
    {
        "chainId": chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": my_address,
        "nonce": nonce,
    }
)
# print(transaction)

signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
# print(signed_txn)

# Send transaction
print("Deploying contract...")
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("Deployed")
# working with the contract : One need always: contract address, contract abi
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
# Call -> Simulate making the call and getting a return value
# Transact -> Actually make a state change

# Initial value of favourite number
print(simple_storage.functions.retrieve().call())
# print(simple_storage.functions.store(15).call())
print("Updating contract...")
store_transaction = simple_storage.functions.store(15).buildTransaction(
    {
        "chainId": chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": my_address,
        "nonce": nonce + 1,
    }
)

signed_store_txn = w3.eth.account.sign_transaction(
    store_transaction, private_key=private_key
)
send_store_tx = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)
print("Updated")
print(simple_storage.functions.retrieve().call())
