# Status and Next Steps

This is an early and incomplete protocol design proposal. It has not been well vetted for feasibility and safety. It has not had broad review from the Zcash community, so its status on any Zcash roadmap is undetermined.

## Current Components

### This Book

This book is intended to become both a high-level overview and introduction to [TFL](../terminology.md#definition-tfl), and a full specification.

### Crosslink

The current heart of the design work is an in-progress hybrid consensus protocol construction called [Crosslink (definition)](../terminology.md#definition-crosslink). This is defined in the [Crosslink chapter](../design/crosslink.md).

### `simtfl`

We've begun creating a simulator called [`simtfl`](../terminology.md#definition-simtfl) which we will use to model security and abstract performance concerns. Its development is tracked at <https://github.com/zcash/simtfl>.

## Major Missing Components

- PoS subprotocol selection,
- Issuance and supply mechanics, such as how much ZEC stakers may earn,
- Integrated Zcash transaction semantics,
- A transition plan from current Zcash mainnet to this protocol design,
- [ZIP](../terminology.md#definition-zip)s specifying the above to the level of specificity required by ZIPs,
- Security and safety analyses,
- Economic analyses.

This list may be incomplete, and as the design matures the need for major new components may be revealed.

## Next Steps

This design proposal is being developed by [Electric Coin Company](https://electriccoin.co/) and [Shielded Labs](https://x.com/shieldedlabs) as the first major milestone in our focus of deploying Proof-of-Stake to the Zcash protocol. Our rough near-term plan for this proposal is as follows:

1. Complete the [Crosslink](../terminology.md#definition-crosslink) description.
2. Complete core security arguments for [Crosslink](../terminology.md#definition-crosslink).
3. Define the [Major Missing Components](#major-missing-components) above, including considerations such as issuance mechanics and Proof-of-Stake mechanisms.
4. Complete auxillary security arguments and analyses, such as specific attack scenarios, game-theoretic security, and so forth.
5. Mature [`simtfl`](../terminology.md#definition-simtfl) to analyze all cases of interest.
6. Follow the general Zcash process for proposal/review/refinement, including proposing one or more [ZIP](../terminology.md#definition-zip)s.
7. Follow the general Zcash governance process for proposal review and refinement.
8. If accepted, productionize the proposal in ECC products and collaborate with other implementors who implement the proposal.
9. Celebrate when and if the proposal is activated on Mainnet. 🎉

The fine-grained day-to-day goals and tasks for this project are present in [the Zcash Developers Hub](https://zcash.github.io/developers) in the [TFL-focused DAG](https://zcash.github.io/developers/zcash-tfl-dag).

Please also see [Get Involved](./get-involved.md) if you are interested in tracking this progress more closely, or in contributing.
