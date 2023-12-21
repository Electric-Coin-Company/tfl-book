# Design Overview

This design augments the existing Zcash Proof-of-Work (PoW) network with a new consensus layer which provides *trailing finality*, called the *Trailing Finality Layer (TFL)*.

This layer enables blocks produced via PoW to become *final* which ensures they may never be rolled back. This enables safer and simpler wallets and other infrastructure, and aids trust-minimized cross-chain bridges.

This consensus layer uses a finalizing *Proof-of-Stake (PoS)* consensus protocol, and enables ZEC holders to earn protocol rewards for contributing to the security of the Zcash network. By integrating a PoS layer with the current PoW Zcash protocol, this design specifies a *hybrid consensus protocol*.

The integration of the current PoW consensus with the TFL produces a new top-level consensus protocol referred to as *PoW+TFL*.

In the following subchapters we introduce the [Design at a Glance](./overview/design-at-a-glance.md), then provide an overview of the major components of the design.

Following this overview chapter, we proceed into a detailed [Protocol Specification (TODO)]().

