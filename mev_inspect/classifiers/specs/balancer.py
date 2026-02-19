from typing import List, Optional

from mev_inspect.chain_config import (
    BALANCER_CONTRACT_ADDRESSES,
    PHUX_CONTRACT_ADDRESSES,
    PHUX_VAULT_ADDRESS,
)
from mev_inspect.classifiers.helpers import create_swap_from_pool_transfers
from mev_inspect.schemas.classifiers import ClassifierSpec, SwapClassifier
from mev_inspect.schemas.swaps import Swap
from mev_inspect.schemas.traces import DecodedCallTrace, Protocol
from mev_inspect.schemas.transfers import Transfer

BALANCER_V1_POOL_ABI_NAME = "BPool"


class BalancerSwapClassifier(SwapClassifier):
    @staticmethod
    def parse_swap(
        trace: DecodedCallTrace,
        prior_transfers: List[Transfer],
        child_transfers: List[Transfer],
    ) -> Optional[Swap]:

        recipient_address = trace.from_address

        swap = create_swap_from_pool_transfers(
            trace, recipient_address, prior_transfers, child_transfers
        )
        return swap


class PhuxSwapClassifier(SwapClassifier):
    @staticmethod
    def parse_swap(
        trace: DecodedCallTrace,
        prior_transfers: List[Transfer],
        child_transfers: List[Transfer],
    ) -> Optional[Swap]:
        # funds tuple: (sender, fromInternalBalance, recipient, toInternalBalance)
        funds = trace.inputs["funds"]
        recipient_address = funds[2]

        return create_swap_from_pool_transfers(
            trace, recipient_address, prior_transfers, child_transfers
        )


BALANCER_V1_SPECS = [
    ClassifierSpec(
        abi_name=BALANCER_V1_POOL_ABI_NAME,
        protocol=Protocol.balancer_v1,
        classifiers={
            "swapExactAmountIn(address,uint256,address,uint256,uint256)": BalancerSwapClassifier,
            "swapExactAmountOut(address,uint256,address,uint256,uint256)": BalancerSwapClassifier,
        },
    ),
]

PHUX_VAULT_SPEC = ClassifierSpec(
    abi_name="BalancerVault",
    protocol=Protocol.phux,
    valid_contract_addresses=[PHUX_VAULT_ADDRESS],
    classifiers={
        "swap((bytes32,uint8,address,address,uint256,bytes),(address,bool,address,bool),uint256,uint256)": PhuxSwapClassifier,
    },
)

PHUX_SPECS = [PHUX_VAULT_SPEC] if PHUX_CONTRACT_ADDRESSES else []

BALANCER_CLASSIFIER_SPECS = (
    ([*BALANCER_V1_SPECS] if BALANCER_CONTRACT_ADDRESSES else []) + PHUX_SPECS
)
