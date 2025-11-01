from ecdsa import SigningKey, SECP256k1


class Wallet:
    def __init__(self):
        self.private_key = SigningKey.generate(curve=SECP256k1)
        self.public_key = self.private_key.get_verifying_key()

        self.private_key_hex = self.private_key.to_string().hex()
        self.public_key_hex = self.public_key.to_string().hex()

        self.address = self.public_key_hex[:32]

    def mint(self, nft):
        pass

    @staticmethod
    def from_private_key_hex(private_key_hex):
        wallet = Wallet()

        private_key_bytes = bytes.fromhex(private_key_hex)
        wallet.private_key = SigningKey.from_string(private_key_bytes, curve=SECP256k1)
        wallet.public_key = wallet.private_key.get_verifying_key()

        wallet.private_key_hex = wallet.private_key.to_string().hex()
        wallet.public_key_hex = wallet.public_key.to_string().hex()

        wallet.address = wallet.public_key_hex[:32]

        return wallet