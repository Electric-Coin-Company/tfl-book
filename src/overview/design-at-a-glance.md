# Design at a Glance

The [PoW+TFL](../terminology.md#definition-pow-tfl) consensus protocol is logically an extension of the Zcash consensus rules to introduce [trailing finality](../terminology.md#definition-trailing-finality). This is achieved by compartmentalizing the top-level PoW+TFL protocol into two [consensus subprotocols](../terminology.md#definition-consensus-subprotocols), one embodying most of the current consensus logic of Zcash and another the TFL. These protocols interact through a [hybrid construction](../terminology.md#definition-hybrid-construction), which specifies how the protocols interact, and what changes from "off-the-shelf" behavior, if any, need to be imposed on the subprotocols. Each of these components (the two subprotocols and the hybrid construction) are somewhat modular: different subprotocols or hybrid constructions may be combined (with some modification) to product a candidate [PoW+TFL](../terminology.md#definition-pow-tfl) protocol.

**TODO:** Add consensus subprotocol diagram.

## Hybrid Construction

The [hybrid construction](../terminology.md#definition-hybrid-construction) is a major design component of the full consensus protocol which specifies how the subprotocols integrate. So far we have considered three candidates:

1. The implied/loosely defined hybrid construction presented at Zcon4. **TODO: Link**
2. The [Snap-and-Chat](../terminology.md#definition-snap-and-chat) from the Ebb-and-Flow paper. **TODO: Add References and link.**
3. The [Crosslink](../terminology.md#definition-crosslink) construction.

Currently we believe [Crosslink](../terminology.md#definition-crosslink) is the best candidate, due to security considerations.

**TODO:** Clarify the security considerations at a high level.

## Subprotocols

The PoW+TFL hybrid consensus consists of two interacting subprotocols:

1. [PoW Subprotocol](../terminology.md#definition-pow): this subprotocol is very similar to NU5 consensus. It is a design goal of the TFL design to minimize changes to this subprotocol. Note: the shorthand "PoW" is potentially misleading, because this subprotocol is also responsible for the bulk of all supply and transaction semantic consensus rules.
2. [PoS Subprotocol](../terminology.md#definition-pos): this is a new subprotocol which provides trailing finality via a finalizing PoS protocol.

**TODO:** Find a more precise name for the PoW subprotocol, because this subprotocol is responsible for:
- Proof-of-Work proving/validation (unmodified)
- Nakamoto Best-chain Fork Choice rule (potentially modified by the [hybrid construction](../terminology.md#definition-hybrid-construction))
- Transaction Validity Rules (with a [transaction context](../terminology.md#definition-hybrid-construction) potentially modified by [hybrid construction](../terminology.md#definition-hybrid-construction))

Note that the [hybrid construction](../terminology.md#definition-hybrid-construction) may require modification to the "off-the-shelf" versions of these subprotocols. In particular [Crosslink](../terminology.md#definition-crosslink) requires each protocol to refer to the state of the other to provide [objective validity](../terminology.md#definition-objective-validity).
