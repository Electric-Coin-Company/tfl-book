# Design Goals

Here we strive to lay out our high level TFL design goals.

## User Experience and Use Case Goals

We strive to start our protocol design process from user experience (UX) and use case considerations foremost, since at the end of the day all that matters in a protocol is what user needs it meets and how well.

- All currently supported wallet user experience should continue to operate seamlessly without change during or after protocol transitions. This covers the use of addresses, payment flow, transfers, ZEC supply cap and issuance rate, backup/restore, and other features users currently rely on.
- There must be no security or safety degradation due to wallet user behavior introduced by PoS transitions, assuming users follow their current behaviors unchanged and continue to use the same cognitive model of the impacts of their behaviors. This goal encompasses all of security and safety, including privacy and transparency or more explicit disclosures.
- The protocol should enable users of shielded mobile wallets to delegate ZEC to PoS consensus providers and earn a return on that ZEC coming via ZEC issuance or fees. Doing this may expose users to a risk of loss of delegated ZEC (such as through “slashing fees”). The protocol must guarantee that PoS consensus providers have no discretionary control over such delegated funds (including that they cannot steal those funds).
- For any hybrid PoW/PoS protocol (including the PoW+TFL protocol we’re proposing), the process and UX of mining remains unchanged except that the return on investment may be altered. This is true both of consensus level block miners (ie mining pools and solo miners) and mining pool participants.
- The any hybrid PoW/PoS protocol (including PoW+TFL) block explorers will continue to function with the same UX through transitions in-so-far as displaying information about transactions, the mempool, and blocks.
- Block explorers and other network metrics sites may require UX changes with respect to mining rewards and issuance calculations.
- Network metrics sites may require UX changes with respect to the p2p protocol or other network-specific information.

## Developer Experience Goals

For a full PoS transition, ecosystem developers for products such as consensus nodes, wallets, mining services, chain analytics, and more will certainly need to update their code to support transitions. However, we carve out a few goals as an exception to this for this category of users:

- Wallet developers should not be required to make any changes through protocol transitions as long as they rely solely on the lightwalletd protocol or a full node API (such as the zcashd RPC interface).
- For any hybrid PoW/PoS protocol (including PoW+TFL), mining pools and miners should not be required to make any software or protocol changes as long as they rely on zcashd-compatible GetBlockTemplate. One exception to this is software that bakes in assumptions about the block reward schedule, rather than relying on GetBlockTemplate solely.

## Safety, Security, and Privacy Goals

Zcash has always had exemplary safety, security, and privacy, and we aim to continue that tradition:

- For any hybrid PoW/PoS protocol (including PoW+TFL), the cost-of-attack for a 1-hour rollback should not be reduced, given a “reasonably rigorous” security argument.
- For any hybrid PoW/PoS protocol (including PoW+TFL), the cost-of-attack to halt the chain should be larger than the 24 hour revenue of PoW mining rewards, given a “reasonably rigorous” security argument.

TODO: privacy, pure-PoS security goals.

## Design Conservatism Goals

We want to follow some conservative design heuristics to minimize risk and mistakes:

- Rely as much as possible on design components that are already proven in production environments.
- Rely as much as possible on design components with adequate theoretical underpinnings and security analyses.
- Minimize changes or variations on the above: strive to only alter existing work when necessary for overall design goals. For example, Zcash's privacy or issuance constraints are likely less common among existing PoS designs.
