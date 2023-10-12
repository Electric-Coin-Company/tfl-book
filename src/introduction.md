# A Trailing Finality Layer for Zcash

This book introduces and specifies a [*Trailing Finality Layer*](./terminology.md#definition-tfl) for the Zcash network.

This design augments the existing Zcash Proof-of-Work ([PoW](./terminology.md#definition-pow)) network with a new consensus layer which provides [*trailing finality*](./terminology.md#definition-trailing-finality). This layer enables transactions included via PoW to become [*final*](./terminology.md#definition-final) which ensures they may never be rolled back. This enables safer and simpler wallets and other infrastructure, and aids trust-minimized cross-chain bridges. This consensus layer uses [*Proof-of-Stake*](./terminology.md#definition-pos) consensus, and enables ZEC holders to earn protocol rewards for contributing to the security of the Zcash network. By integrating a PoS layer with the current PoW Zcash protocol, this design specifies a [*hybrid consensus*](./terminology.md#definition-hybrid-consensus) protocol dubbed [PoW+TFL](./terminology.md#definition-pow-tfl).

The rest of this introductory chapter is aimed at a general audience interested in the context of this proposal within Zcash development, status and next steps, motivations, a primer on finality, and tips to get involved.
