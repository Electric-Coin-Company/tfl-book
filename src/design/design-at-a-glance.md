# Design at a Glance

The [PoW+TFL](../terminology.md#definition-pow-tfl) consensus protocol is logically an extension of the Zcash consensus rules to introduce [trailing finality](../terminology.md#definition-trailing-finality). This is achieved by compartmentalizing the top-level PoW+TFL protocol into two [consensus subprotocols](../terminology.md#definition-consensus-subprotocols), one embodying most of the current consensus logic of Zcash and another the TFL. These protocols interact through a [hybrid construction](../terminology.md#definition-hybrid-construction), which specifies how the protocols interact, and what changes from "off-the-shelf" behavior, if any, need to be imposed on the subprotocols. Each of these components (the two subprotocols and the hybrid construction) are somewhat modular: different subprotocols or hybrid constructions may be combined (with some modification) to produce a candidate [PoW+TFL](../terminology.md#definition-pow-tfl) protocol.

**TODO:** [Add a protocol component diagram to "Design at a Glance" #122](https://github.com/Electric-Coin-Company/tfl-book/issues/122)

## Hybrid Construction

The [hybrid construction](../terminology.md#definition-hybrid-construction) is a major design component of the full consensus protocol which specifies how the subprotocols integrate. So far we have considered three candidates:

1. The implied/loosely defined hybrid construction [presented at Zcon4](https://www.youtube.com/watch?v=qhMzMYeEPMM&list=PL40dyJ0UYTLII7oQRQmNOFf0d2iKT35tL&index=17).
2. The [Snap-and-Chat](../terminology.md#definition-snap-and-chat) from the [Ebb-and-Flow paper](https://eprint.iacr.org/2020/1091).
3. The [Crosslink](../terminology.md#definition-crosslink) construction.

We believe [Crosslink](../terminology.md#definition-crosslink) is the best candidate, due to its more rigorous [specification](./crosslink/construction.md) and [security analysis](./crosslink/security-analysis.md).

## Subprotocols

The PoW+TFL hybrid consensus consists of two interacting subprotocols:

1. [PoW Subprotocol](../terminology.md#definition-pow): this subprotocol is very similar to NU5 or NU6 consensus. It is a design goal of the TFL design to minimize changes to this subprotocol. Note: the shorthand "PoW" is potentially misleading, because this subprotocol is also responsible for the bulk of all supply and transaction semantic consensus rules.
2. [PoS Subprotocol](../terminology.md#definition-pos): this is a new subprotocol which provides trailing finality via a finalizing PoS protocol.

**TODO:** [Clarify the distinctions between pure PoW, the PoW subprotocol, NU6, and fork-choice vs all of transaction semantics. #119](https://github.com/Electric-Coin-Company/tfl-book/issues/119)

Note that the [hybrid construction](../terminology.md#definition-hybrid-construction) may require modification to the "off-the-shelf" versions of these subprotocols. In particular [Crosslink](../terminology.md#definition-crosslink) requires each protocol to refer to the state of the other to provide [objective validity](../terminology.md#definition-objective-validity).
