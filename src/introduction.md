# A Trailing Finality Layer for Zcash

This book introduces and specifies a *Trailing Finality Layer* for the Zcash network.

This design augments the existing Zcash Proof-of-Work (PoW) network with a new consensus layer which provides *trailing finality*. This layer enables blocks produced via PoW to become *final* which ensures they may never be rolled back. This enables safer and simpler wallets and other infrastructure, and aids trust-minimized cross-chain bridges. This consensus layer uses Proof-of-Stake consensus, and enables ZEC holders to earn protocol rewards for contributing to the security of the Zcash network. By integrating a PoS layer with the current PoW Zcash protocol, this design specifies a *hybrid consensus protocol*.

See how to [Get Involved](./introduction/get-involved.md).

## Status

This is an early and very incomplete protocol design proposal. It has not been well vetted for feasibility and safety. It has not had broad review from the Zcash community, so its status on any Zcash roadmap is undetermined.

### Major Missing Elements

This design is at a very early stage and lacks substantial clarity around essential details. These details must be clarified before this proposal would be ready for the [Zcash Improvement Proposals](https://zips.z.cash) process. They include:

- PoS protocol selection,
- Issuance and supply mechanics, such as how much ZEC stakers may earn,
- A transition plan from current Zcash mainnet to this protocol design,
- The specifics of how PoW and PoS safely integrate,
- Security and safety analysis,
- Economic analysis,
- and more.

## Next Steps

This design proposal is being developed by [ElecticCoin Co](https://electriccoin.co/) as the first major milestone in our focus of deploying Proof-of-Stake to the Zcash protocol. Our rough near term plan for this proposal is as follows:

1. Write a very high-level design overview which lacks many details but clarifies the general approach.
2. Get early feedback from Zcash community and consensus protocol experts on this high level overview.
3. If there are flaws so substantial that we decide the approach is infeasible, start over with a different PoS transition design.
4. Otherwise, refine the high-level "overview" into a concrete, comprehensive proposal through multiple milestones with wide review.
5. As the concrete proposal approaches maturity, draft one or more [Zcash Improvement Proposals](https://zips.z.cash).
6. Follow the general Zcash process for proposal/review/refinement.
7. Follow the general Zcash governance process for proposal acceptance.
8. If accepted, productionize the proposal in ECC products and collaborate with other implementors who implement the proposal.
9. Celebrate when the proposal is activated on Mainnet. 🎉
