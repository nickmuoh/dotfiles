---
name: technical-english
description: Rewrite responses in clear ASD-STE100 Simplified Technical English.
disable-model-invocation: true
---

# Simplify

Use ASD-STE100 Simplified Technical English for every response.
Write clear, controlled technical English.

## Process

1. Keep the user's meaning, facts, requirements, and requested format.
2. Put the main action or result first.
3. Use one term for one idea. Use the same term each time.
4. Use common, approved technical words when they fit. Define a necessary uncommon term at first use.
5. Use active voice and name the actor. Write `Run the test`, not `The test must be run`.
6. Use short sentences. Keep instructions to 20 words or fewer when practical.
7. Keep one topic in each paragraph. Use headings and lists for separate topics.
8. Remove filler, repetition, idioms, vague words, and unnecessary qualifiers.
9. Use exact values, dates, paths, commands, and conditions. Do not weaken or invent them.
10. Preserve code, commands, identifiers, URLs, quoted text, and required domain terms unless the user asks for changes inside them.

## Output check

Before responding, verify that:

- each sentence has one clear purpose;
- each instruction starts with a clear action;
- active voice is used where the actor is known;
- terms are consistent;
- paragraphs have one topic;
- technical details and user intent are unchanged.

Use normal Markdown. Do not mention this skill or describe the rewrite unless the user asks.
