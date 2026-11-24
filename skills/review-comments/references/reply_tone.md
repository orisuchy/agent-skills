# Reply tone guide

Default tone: the user is a junior developer; reviewers are seniors. Replies should sound like a teammate
who took the feedback seriously, not a defensive response and not a sycophantic one.

## Principles

- **Short.** 1–3 sentences. For trivial fixes a single word like "Done!" is fine.
- **Concrete when context helps.** If the change isn't obvious from the diff, say what was
  done so the reviewer doesn't have to re-read it. If the change is a 1-line obvious fix,
  "Done!" is enough.
- **Technical, not chatty.** Mention the specific function, class, parameter, or behavior
  involved when it adds signal.
- **Polite, not effusive.** No "great catch!", no "thanks so much for the thoughtful review!".
  A single "thanks" is fine when the reviewer pointed out something genuinely non-obvious.
- **Honest disagreement is OK.** If the reviewer's suggestion isn't right, explain the reason
  in one sentence. Ask for their take rather than asserting — they have more context.

## Templates

### When the fix was applied

Trivial / obvious fix (typo, rename, removed unused import, single-line tweak):

> Done!

Non-trivial fix — say what was done:

> Fixed — extracted the retry logic into `withRetry` so callers don't duplicate it.

> Updated to use `Optional<>` here. Removed the null check on the caller side too.

> Good point, switched to `computeIfAbsent` so the lookup is atomic.

### When something was applied but with a small twist

> Done, though I kept the `default` branch since `X` is exhaustive only in the new enum —
> the older callers still pass legacy values.

### When pushing back

> I'd lean toward keeping it inline here — the helper would only have one caller and the
> branch is short. Happy to extract it if you'd rather; let me know.

> The null check is intentional: `getFoo()` can return null when the cache is cold (see
> `FooCache#load`). I can add a comment if that's not obvious.

### When asking for clarification

> Want to make sure I'm reading this right — are you suggesting we move the validation into
> the constructor, or keep it where it is and just rename the method?

### When the reviewer is right and the original code was wrong

> You're right, that was a leftover from the previous approach. Removed.

## Anti-patterns

- ❌ "Thanks for the great feedback! I really appreciate you taking the time…" — sycophantic.
- ❌ "I'll fix this in a follow-up." — only acceptable if there's a tracked ticket; include the link.
- ❌ Long explanations of *why* the original code looked the way it did. The reviewer doesn't
  need history; they need to know the current state.
- ❌ Restating the reviewer's comment back to them.
