# A Path to Proof-of-Stake Zcash

This Trailing Finality Layer (TFL) design provides a possible first step in transitioning [Zcash](https://z.cash) to a Proof-of-Stake (PoS) protocol. Here we describe how a transition to PoS relates to "the Zcash roadmap" and how TFL fits into one approach to a PoS transition.

## The Zcash Tech-Tree

There are multiple developer orgs working on different proposed features for Zcash. Some of these involve multiple large distinct upgrade steps, and several of these steps depend on other such steps. This could be represented as a directed-acyclic graph. We have begun referring to this space of possible future improvements as the *Zcash Tech-Tree*, taking inspiration from an analogous concept in gaming.[^tech-tree-history]

We envision a *proof-of-stake transition path* as one of the potential paths within this tech-tree which is the primary protocol focus of this proposal.

## A Proof-of-Stake Transition Path

Given that context, we envision a "path" within the Zcash Tech-Tree for transitioning Zcash to PoS. At the top-level we propose this path contains at least two major milestones:

1. Transitioning from current Zcash PoW to a hybrid PoW/PoS system.
2. Transitioning from a hybrid PoW/PoS system to pure PoS.

Our primary motivation for proposing (at least) two steps is to minimize usability, safety, security, and ecosystem distruption during each step.

### Design Goals for a Hybrid PoW/PoS System

We are refining the design of TFL with several design goals in mind:

- We want minimal-to-no disruption for existing wallet use cases and UX. For example, nothing should change for the user flows for storing or transferring funds, the format of addresses, etc…
- We want a security analysis of the proposed protocol to be as simple as possible _given_ existing security analyses of current Zcash.
- We want to enable new use cases around PoS that allow mobile shielded wallet users to earn a return on delegated ZEC.
- We want to enable trust-minimized bridges and other benefits by providing a protocol with _absolute finality_. 
- We want to improve the _modularity_ of the consensus protocol, which has several loosely defined and related meanings, e.g.: it's possible to understand some consensus properties only given knowledge of a "component" of the protocol, and it's possible to implement consensus rules in modular code components with clean interfaces.

We will be refining these goals and potentially adding more as we continue to develop this proposal.

## Trailing Finality Layer in a Nutshell

The Zcash Trailing Finality Layer refers to a new subprotocol of a new hybrid PoW/PoS protocol, which we refer to as *PoW+TFL*. This subprotocol introduces *absolute finality* for the Zcash blockchain, ensuring that *final* blocks (and the transactions within them) may never be rolled back.

This design is appealing as a safer first step in transitioning the Zcash protocol for multiple reasons:

### Minimal Use-Case Disruption

First of all, in many cases, existing products, services, and tools can continue using the mainnet chain with no changes to code assuming they rely on existingn consensus nodes. We view this as a major benefit which allows Zcash's existing user network effect to continue safely unperturbed.

There will be certain narrow exceptional areas if those products, services, or tools need to be precise in areas where the protocol has changed, such as issuance schedules, transaction formats, or chain rollback logic.

### Minimal Consensus Rule Changes

Outside of PoS mechanics (such as bonding/unbonding stake, delegating, etc…), and changes to issuance (due to supporting both PoS and PoW) this design adds precisely one consensus rule:

> Final blocks may not be rolled back.

We believe this presents a minimal change to consensus rules to enable PoS, and is thus one of the safest approaches to a transition in terms of security analysis.

### Modular Design

By conceptualizing the TFL as a distinct "layer" or subprotocol, the consensus rules can be described as the explicit interactions between two subprotocols, one similar to the existing Zcash protcol as of NU5, and the other as a finalizing PoS protocol.

This approach helps in reasoning about failure modes, and how global consensus properties are achieved by which subprotocols.

Finally, since one subprotocol is very similar to the existing Zcash NU5 protocol, this lessons risk that the consensus properties within that subprotocol compromise current NU5 properties. 

### Modular Implementation

In addition to the other benefits of protocol design modularity, we anticipate actual implementations can realize this modularity in code. This can help makes implementations more robust, easier to maintain, and more interoperable.

 For example, we can envision a standardized interface between PoW & TFL consensus components, enabling different development teams to provide these different components and for "full node" packagers to mix and match them. This is somewhat reminiscent of Ethereum's execution/consensus layer separation which we believe has shown great success in implementation team and product diversity.


---

[^tech-tree-history]: See [Wikipedia's Technology Tree - History](https://en.wikipedia.org/wiki/Technology_tree#History) section for details.

