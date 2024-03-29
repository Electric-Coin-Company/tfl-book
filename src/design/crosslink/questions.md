# Questions about Crosslink

### Why don't we have a bc‑block‑validity rule snapshot(LF(H)) ⪯<sub>bc</sub> H ?

Rationale: Can we outright prevent rollbacks > $\sigma$ from ever appearing in $\mathsf{Ch}_i^t$ ?

Daira Emma: In a variant of Crosslink with this rule, an adversary's strategy would be to keep the $\mathsf{context\_bft}$ fields in its blocks as $C$ such that $B = \textsf{bft-last-final}(C)$ when the attack starts, and then fork from the bc-best-chain that extends $\mathsf{snapshot}(B)$. If its private chain falls behind the public bc-best-chain, it resets, just like in a conventional private mining attack.

Note that the proposed rule does *not* prevent the adversary's private chain from just staying at the same $\mathsf{context\_bft}$ block. The reason is that Crosslink does not change the fork-choice rule of $\Pi_{\mathrm{bc}}$. That is, even if the adversary's chain has a $\mathsf{context\_bft}$ that is far behind the current bft-block, it is still allowed to become the bc-best-chain.

(Eventually the adversary's chain using this strategy will hit the finality gap bound of $L$ blocks. But that must be significantly greater than $\sigma$, to avoid availability problems. So it does not prevent the adversary from performing a rollback longer than $\sigma$ blocks before they hit the bound. Also, going into Safety Mode for new blocks does not prevent the attacker's chain from having included harmful transactions before that point.)

It is possible to change the fork-choice rule, for example so that the bc-best-chain for a node $i$ is required to extend $\mathsf{snapshot}(B)$ where $B$ is the last final block for any bft-chain in node $i$'s view.

This would break the current safety and liveness arguments for Crosslink. But for the sake of argument, suppose we did it anyway.

The adversary's strategy would change slightly: it resets if *either* its private chain falls behind the public bc-best-chain, or its private chain is invalidated because it forks before $\mathsf{snapshot}(B)$ for some new last final block $B$ of a bft-chain. During the attack, it also attempts to impede progress of the BFT protocol as far as possible.

In that case, the proposed rule still does not preclude a rollback of more than $\sigma$ blocks, for several reasons:
* In general we can't say anything about how many bc-blocks are mined in any given interval, so it could be the case that more than $\sigma$ blocks are mined on both the honest chain and the adversary's chain before it would be realistically possible to go through even a single round of the BFT protocol.
* Nor can we say anything about how quickly those blocks are finalized, unless we enforce it, which we don't. (In Crosslink we do enforce a finalization gap bound $L$, but as explained above $L$ must be significantly greater than $\sigma$, so that doesn't really help.)
  * In particular, the adversary could be suppressing publication of final bft-blocks, or attacking the *liveness* of the BFT protocol in other ways. An attack against BFT liveness is potentially easier than an attack against BFT safety, and it would be difficult to characterise exactly how much this rule gains you in terms of security given that (at best) it's dependent on that.
* $\mathsf{snapshot}(\mathsf{LF}(H))$ will typically be at least $\sigma + 1$ blocks back from $H$.
  The argument for that goes:
  > None of the block hashes in $\mathsf{LF}(H)\mathsf{.headers\_bc}$ can point to $H$ because that would be a hash cycle. In a typical case where no block withholding and no *other* rollback (not caused by the adversary) occurs on the honestly mined chain, the proposer of the last final block before a context bft-block that $H$ can point to will have, at the latest, $H \lceil_{\mathrm{bc}}^1$ as $\mathsf{tip}(B)$. Under these conditions, $\mathsf{snapshot}(\mathsf{LF}(H))$ will point, at the latest, to $\sigma$ blocks before $H \lceil_{\mathrm{bc}}^1$, i.e. $\sigma + 1$ blocks before $H$.
  >
  This means that by the time $\mathsf{snapshot}(\mathsf{LF}(H))$ could catch up to $H$, on average $\sigma + 1$ block times will have occurred. So, roughly speaking, the rule that $\mathsf{snapshot}(\mathsf{LF}(H)) \preceq_{\mathrm{bc}} H$ does not usefully constrain the adversary until after $\sigma + 1$ block times. Wlog let's assume $\Pi_{\mathrm{bc}}$ uses PoW: if $\sigma$ is chosen reasonably, then being able to do a $\sigma + 1$-block rollback at all probably requires having somewhere close to 50% of network hash rate. And so in $\sigma + 1$ block times the adversary has a significant chance of being able to do the required rollback before the suggested rule "kicks in". (It also has however much additional latency is added by the BFT protocol, which is simultaneously under attack to maximise this latency.)

All that said, does the suggested rule help? First we have to ask whether it introduces any weaknesses.
  * One potential issue is that the rule cuts both ways: if an adversarial rollback of more than $\sigma$ blocks *does* occur, then the adversary can make a proposal that will "lock in" its success. But it can be argued that this is intended behaviour anyway: the adversary has a confirmed chain, and is entitled to propose to finalize it.
  * What happens if $\Pi_{\mathrm{bft}}$ is broken?
    * **Edit: the answer below refers to Crosslink before the Increasing Score rule was added.**
    * This could definitely be a problem. If either an adversary has a two thirds supermajority of validators, *or* $\Pi_{\mathrm{bft}}$ is completely broken (e.g. by a bug in the implementation of the validation signature scheme), then they can add a final block to the bft-chain with a $\mathsf{headers\_bc}$ field that does not satisfy the honest voting condition. They do not need this to be bft-valid (although greater vulnerability to bugs in the implementation of bft-validity are also an issue). Then they can use the proposed rule to prevent an arbitrary bc-valid-chain from being extended (e.g. by mining $\sigma + 1$ blocks from $\mathcal{O}_{\mathrm{bc}}$ at the genesis difficulty, then getting that chain into a final bft-block). **[Edit: they would no longer be able to do this using a chain mined at a much lower difficulty, because of the Increasing Score rule.]**
      * In Crosslink, this is very carefully avoided. The only similar rule that depends on $\mathsf{snapshot}(\mathsf{LF}(H))$ and that could potentially affect liveness of $\Pi_{\mathrm{bc}}$ is the [**Finality depth**](./construction.md#%CE%A0bc-block-validity) rule. But that rule *always* allows the alternative of producing a Safety Mode block on the current bc-best-chain --- and honest block producers will do so. Therefore, the effect of trying to exploit even a catastrophic break in $\Pi_{\mathrm{bft}}$ in order to cause a rollback of $\mathsf{LOG}_{\mathrm{fin}}$, as long as $\Pi_{\mathrm{bc}}$ has not also been broken, is to go into Safety Mode.
      * This does not mean that a break of $\Pi_{\mathrm{bft}}$ is not a problem for Crosslink. In particular, an adversary that can violate safety of $\Pi_{\mathrm{bft}}$ can violate safety of $\mathsf{LOG}_{\mathrm{bda}}$ (and of $\mathsf{LOG}_{\mathrm{fin}}$ if there is also a $\sigma$-block rollback in some node's bc-best-chain).
      * The difference is that a safety violation of $\Pi_{\mathrm{bft}}$ can be directly observed by nodes *without any chance of false positives*, which is not necessarily the case for all possible attacks against $\Pi_{\mathrm{bft}}$. (The attack described above does *not* violate safety of $\Pi_{\mathrm{bft}}$; it just adds a final bft-block with a suspiciously long $\Pi_{\mathrm{bc}}$ rollback. It could alternatively have added a block with a less suspiciously long rollback, say exactly $\sigma + 1$ blocks. That is, in pursuit of preventing an attack against $\Pi_{\mathrm{bc}}$, we have enabled attacks against $\Pi_{\mathrm{bft}}$ to achieve the same effect --- precisely what Crosslink is designed to prevent.)
      * This raises an interesting idea: if any node sees a rollback in the chain of final bft-blocks, it could provide objective evidence of that rollback in the form of a "bft-final-vee": two final bft-blocks with the same parent. Similarly, if any node sees more than one third of stake vote for conflicting blocks in a given epoch, then the assumption bounding the adversary's stake must have been violated. This evidence can be posted in a transaction to the bc-chain. In that case, any node that is synced to the bc-chain can see that the bft-chain suffered a violation of safety or of a safety assumption, without needing to have seen that violation itself. This can be generalized to allow other proofs of flaws in $\Pi_{\mathrm{bft}}$. Optionally, a bc-chain that has posted such a proof could be latched into Safety Mode until manual intervention can occur. (Obviously we need to make sure that this cannot be abused for denial-of-service.)
      * This is now described in [Potential changes to Crosslink](./potential-changes.md#recommended-recording-more-info-about-the-bftchain-in-bcblocks).

**Okay, but is it a good idea to make that change to the fork-choice rule anyway?**

Probably not. I don't know how to repair the safety and liveness arguments.

The change was that the bc-best-chain for a node $i$ would be required to extend $\mathsf{snapshot}(B)$ where $B$ is the last final bft-block in node $i$'s view.

From the point of view of any modular analysis that treats $\Pi_{\mathsf{bft}}$ as potentially subverted, we cannot say anything useful about $\mathsf{snapshot}(B)$. It seems as though any repair would have to assume much more about the BFT protocol than is desirable.

In general, changes to fork-choice rules are tricky; it was a fork-choice rule problem that allowed the liveness attack against Casper FFG described in [[NTT2020](https://eprint.iacr.org/2020/1091.pdf), Appendix E].

**What if validators who see that a long rollback occurred, refuse to vote for it?**

Yep that is allowed. The rule is "An honest validator will only vote for a proposal $P$ if ..." (not if-and-only-if). If an honest validator sees a "good" reason not to vote for a proposal, including reasons based on out-of-band information, they should not. The [Complementarity argument](./the-arguments-for-bounded-dynamic-availability-and-finality-overrides.md) made in *The Argument for Bounded Dynamic Availability and Finality Overrides* actually depends on this. Obviously, it may affect BFT liveness (and that's okay).

The only reason why we don't make this part of the voting condition is that it's stateful rule. A new validator could come along and wouldn't have the state needed to enforce it. Perhaps that could be fixed.
