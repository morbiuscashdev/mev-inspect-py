from typing import List, Optional

from mev_inspect.chain_config import (
    PULSEX_V1_ROUTER_ADDRESS,
    PULSEX_V2_ROUTER_ADDRESS,
    UNISWAP_V3_CONTRACT_ADDRESSES,
)
from mev_inspect.classifiers.helpers import create_swap_from_pool_transfers
from mev_inspect.schemas.classifiers import ClassifierSpec, SwapClassifier
from mev_inspect.schemas.swaps import Swap
from mev_inspect.schemas.traces import DecodedCallTrace, Protocol
from mev_inspect.schemas.transfers import Transfer

UNISWAP_V2_PAIR_ABI_NAME = "UniswapV2Pair"
UNISWAP_V3_POOL_ABI_NAME = "UniswapV3Pool"


class UniswapV3SwapClassifier(SwapClassifier):
    @staticmethod
    def parse_swap(
        trace: DecodedCallTrace,
        prior_transfers: List[Transfer],
        child_transfers: List[Transfer],
    ) -> Optional[Swap]:

        recipient_address = trace.inputs.get("recipient", trace.from_address)

        swap = create_swap_from_pool_transfers(
            trace, recipient_address, prior_transfers, child_transfers
        )
        return swap


class UniswapV2SwapClassifier(SwapClassifier):
    @staticmethod
    def parse_swap(
        trace: DecodedCallTrace,
        prior_transfers: List[Transfer],
        child_transfers: List[Transfer],
    ) -> Optional[Swap]:

        recipient_address = trace.inputs.get("to", trace.from_address)

        swap = create_swap_from_pool_transfers(
            trace, recipient_address, prior_transfers, child_transfers
        )
        return swap


# V3 specs are driven by chain_config; empty dict disables all V3 matching.
UNISWAP_V3_CONTRACT_SPECS = [
    ClassifierSpec(
        abi_name=abi_name,
        protocol=Protocol.uniswap_v3,
        valid_contract_addresses=[addr],
    )
    for abi_name, addr in UNISWAP_V3_CONTRACT_ADDRESSES.items()
]

UNISWAP_V3_GENERAL_SPECS = [
    ClassifierSpec(
        abi_name=UNISWAP_V3_POOL_ABI_NAME,
        protocol=Protocol.uniswap_v3,
        classifiers={
            "swap(address,bool,int256,uint160,bytes)": UniswapV3SwapClassifier,
        },
    ),
    ClassifierSpec(
        abi_name="IUniswapV3SwapCallback",
    ),
    ClassifierSpec(
        abi_name="IUniswapV3MintCallback",
    ),
    ClassifierSpec(
        abi_name="IUniswapV3FlashCallback",
    ),
]


UNISWAPPY_V2_CONTRACT_SPECS = [
    ClassifierSpec(
        abi_name="UniswapV2Router",
        protocol=Protocol.pulsex_v1,
        valid_contract_addresses=[PULSEX_V1_ROUTER_ADDRESS],
    ),
    ClassifierSpec(
        abi_name="UniswapV2Router",
        protocol=Protocol.pulsex_v2,
        valid_contract_addresses=[PULSEX_V2_ROUTER_ADDRESS],
    ),
]

UNISWAPPY_V2_PAIR_SPEC = ClassifierSpec(
    abi_name=UNISWAP_V2_PAIR_ABI_NAME,
    protocol=Protocol.uniswap_v2,
    classifiers={
        "swap(uint256,uint256,address,bytes)": UniswapV2SwapClassifier,
    },
)

UNISWAP_CLASSIFIER_SPECS: List = [
    *UNISWAP_V3_CONTRACT_SPECS,
    *UNISWAPPY_V2_CONTRACT_SPECS,
    *UNISWAP_V3_GENERAL_SPECS,
    UNISWAPPY_V2_PAIR_SPEC,
]
