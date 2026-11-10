# Independent review of page copy

One reviewer with fresh context, one round. The reviewer must not see the drafting conversation, the reasoning behind choices, or earlier versions; it judges the copy the way a reader would.

## What to give the reviewer

Only these, pasted in full:

1. The page purpose, audience and primary action (three lines from the brief).
2. The Dutch copy, per block, with headings, link and button labels, SEO title, meta description and alt texts.
3. The voice summary from the `info.get` instructions or `docs/brand/voice.md` (the attributes and the do/don't table, not the whole guide).
4. The "AI tells to remove" section of [writing-nl.md](writing-nl.md).

For a reviewed EN or FR version, swap in that language's copy and tell list.

## Reviewer instruction

Paste this as the reviewer's task:

```
You review website copy before a client sees it. You did not write it.

Check, in this order:
1. Does a visitor in the stated audience get the answer or the main point in the first two sentences, and is the primary action obvious?
2. Any phrase from the AI-tells list, or one that works the same way.
3. Any claim without a fact behind it (adjectives doing the work of proof), or a fact that looks invented.
4. Anything that contradicts the voice summary (address form, formality, words to avoid).
5. Headings, link and button labels that don't say what they lead to.

Report at most 10 findings, most important first, each as:
- "<exact quote>" → problem → suggested rewrite

Then one line: READY or NEEDS WORK. Don't rewrite the whole text and don't praise.
```

## After the review

- Apply findings you agree with.
- For findings you reject, keep a one-line reason and show them to the user next to the copy ("Reviewer suggested X; kept Y because …").
- Don't start a second round. If the verdict was NEEDS WORK and you changed a lot, the user's approval at step 6 is the next check.
