from datetime import datetime

from pydantic import BaseModel, validator

from mev_inspect.chain_config import (
    DAI_TOKEN_ADDRESS,
    HEX_TOKEN_ADDRESS,
    NATIVE_TOKEN_ADDRESS,
    PLSX_TOKEN_ADDRESS,
    USDC_TOKEN_ADDRESS,
    USDT_TOKEN_ADDRESS,
    WRAPPED_NATIVE_TOKEN_ADDRESS,
)

# Aliases used by downstream classifiers
ETH_TOKEN_ADDRESS = NATIVE_TOKEN_ADDRESS
WETH_TOKEN_ADDRESS = WRAPPED_NATIVE_TOKEN_ADDRESS  # WPLS on PulseChain
CETH_TOKEN_ADDRESS = ""  # Compound ETH not deployed on PulseChain

TOKEN_ADDRESSES = [
    ETH_TOKEN_ADDRESS,
    WETH_TOKEN_ADDRESS,
    PLSX_TOKEN_ADDRESS,
    HEX_TOKEN_ADDRESS,
    USDC_TOKEN_ADDRESS,
    USDT_TOKEN_ADDRESS,
    DAI_TOKEN_ADDRESS,
]

COINGECKO_ID_BY_ADDRESS = {
    WETH_TOKEN_ADDRESS: "wrapped-pulse",
    ETH_TOKEN_ADDRESS: "pulsechain",
    PLSX_TOKEN_ADDRESS: "pulsex",
    HEX_TOKEN_ADDRESS: "hex",
    USDC_TOKEN_ADDRESS: "usd-coin",
    USDT_TOKEN_ADDRESS: "tether",
    DAI_TOKEN_ADDRESS: "dai",
}


class Price(BaseModel):
    token_address: str
    usd_price: float
    timestamp: datetime

    @validator("token_address")
    def lower_token_address(cls, v: str) -> str:
        return v.lower()
