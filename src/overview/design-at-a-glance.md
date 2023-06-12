# Design at a Glance

The TFL is logically an extension of the Zcash consensus rules to introduce *trailing finality*. This page is a quick and (currently) hand-wavy summary of TFL from multiple lenses.

Trailing finality depends on a finalizing Proof-of-Stake subprotocol, so the resulting protocol is hybrid PoW+PoS consensus with two *subprotocols*.

## Protocol Terminology

Because we analyze changes from the current protocol to a new hybrid PoW+PoS protocol, and furthermore the new protocol consists of subprotocols, we use the following terminology for distinctions:

- *PoW+TFL*: the overall complete, integrated consensus protocol specified in this book.
- *NU5*: the consensus protocol as of NU5.[^new-mainnet-precursors]
- *PoW*: the PoW subprotocol within PoW+TFL. Note that this is a different consensus protocol from NU5.
- *TFL*: the TFL subprotocol within PoW+TFL.

## Subprotocols

The PoW+TFL hybrid consensus consists of two interacting subprotocols:

1. PoW: this subprotocol is very similar to current Zcash mainnet consensus. It is a design goal of the TFL design to minimize changes to this subprotocol. Note: the shorthand "PoW" is potentially misleading, because this subprotocol is also responsible for the bulk of all supply and transaction semantic consensus rules.
2. TFL: this is a new subprotocol which provides trailing finality via a finalizing PoS protocol.

Fully validating nodes must operate both subprotocols in an integrated manner. These subprotocols follow the design layed out in [Ebb-and-Flow design](../references.md#ebb-and-flow-protocols).

## Design Analysis Focus Areas

Analyzing this design focuses on four areas:

- The design of each subprotocol independently,
- The interaction between the two subprotocols idealized as an interface between subcomponents, and
- The whole as an integrated system.

## Consensus

Consensus is specified in terms of the sub-consensus of each of the two subprotocols, PoW & TFL, along with the interface between the two, and finally in terms of system-wide / integrated consensus rules.

We also explicitly define design goals about which areas of consensus _must not_ be impacted by a transition from NU5 to PoW+TFL.

### Trailing Finality

The TFL extends the Zcash consensus protocol with *Trailing Finality*: TFL *finalizes* blocks that have been produced by PoW. See [Visualizing Trailing Finality](../introduction/visualizing-trailing-finality.md) for an informal description of this.

When focusing on the PoW subprotocol, Trailing Finality introduces minimal changes to the subprotocol consensus: PoW has a mechanism for discovering block finality from TFL, and then it introduces a single new PoW subprotocol consensus rule constraint:

> Rollbacks must not include any final blocks; equivalently: the best PoW chain must include all known final blocks.

There are no other changes to PoW subprotocol consensus specific to trailing finality, including no changes to any ledger rules about balances, transaction semantics, etc…

### Proof-of-Stake

In order to achieve consensus on finality, the TFL uses a PoS protocol which provides absolute finality.

The PoS consensus area is where the bulk of complexity lies in terms of the interface between the PoW and PoS subprotocols because PoW, which is generally responsible for supply and transaction semantics. See [The Subprotocol Interface](#the-subprotocol-interface) below for more detail.

# Footnotes

[^new-mainnet-precursors]: If new consensus changes are deployed to Zcash mainnet prior to PoW+TFL design finalization, this design must be updated to refer to the new delta (e.g. by reanalyzing all changes against NU6 or NU7, etc…)
