# Trailing Finality Layer in a Nutshell

The Zcash Trailing Finality Layer refers to a new subprotocol of a new hybrid PoW/PoS protocol, which we refer to as *PoW+TFL*. This subprotocol introduces *absolute finality* for the Zcash blockchain, ensuring that *final* blocks (and the transactions within them) may never be rolled back.

This design is appealing as a safer first step in transitioning the Zcash protocol for multiple reasons:

## Minimal Use-Case Disruption

First of all, in many cases, existing products, services, and tools can continue using the mainnet chain with no changes to code assuming they rely on existingn consensus nodes. We view this as a major benefit which allows Zcash's existing user network effect to continue safely unperturbed.

There will be certain narrow exceptional areas if those products, services, or tools need to be precise in areas where the protocol has changed, such as issuance schedules, transaction formats, or chain rollback logic.

## Minimal Consensus Rule Changes

Outside of PoS mechanics (such as bonding/unbonding stake, delegating, etc…), and changes to issuance (due to supporting both PoS and PoW) this design adds precisely one consensus rule:

> Final blocks may not be rolled back.

We believe this presents a minimal change to consensus rules to enable PoS, and is thus one of the safest approaches to a transition in terms of security analysis.

## Modular Design

By conceptualizing the TFL as a distinct "layer" or subprotocol, the consensus rules can be described as the explicit interactions between two subprotocols, one similar to the existing Zcash protcol as of NU5, and the other as a finalizing PoS protocol.

This approach helps in reasoning about failure modes, and how global consensus properties are achieved by which subprotocols.

Finally, since one subprotocol is very similar to the existing Zcash NU5 protocol, this lessons risk that the consensus properties within that subprotocol compromise current NU5 properties. 

## Modular Implementation

In addition to the other benefits of protocol design modularity, we anticipate actual implementations can realize this modularity in code. This can help makes implementations more robust, easier to maintain, and more interoperable.

 For example, we can envision a standardized interface between PoW & TFL consensus components, enabling different development teams to provide these different components and for "full node" packagers to mix and match them. This is somewhat reminiscent of Ethereum's execution/consensus layer separation which we believe has shown great success in implementation team and product diversity.
