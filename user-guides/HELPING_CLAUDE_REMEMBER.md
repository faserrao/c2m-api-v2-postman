# How to Help Claude Remember: A Guide for Frank

## Overview
This guide provides specific techniques to help Claude maintain context across sessions and avoid forgetting established work.

## 1. Session Start Reminders

### Begin sessions with context:
```
"We're continuing work on the C2M API pipeline. 
Last session we [specific accomplishment].
Today we need to [current task]."
```

### Reference recent work:
- "Yesterday we implemented token revocation in the JWT script"
- "Last week we fixed the oneOf handling"
- "Remember we always use `make postman-instance-build-and-test`"

## 2. CLAUDE.md Best Practices

### Home Directory CLAUDE.md (~/)
Add a "Current Projects Status" section:
```markdown
## Current Projects Status
### C2M API V2
- JWT script includes token revocation at start (shows complete flow)
- oneOf handling fixed with post-processing scripts
- Use case collection being enhanced with all variants
- Always run pipeline after changes
- Mock responses use meaningful data (not Latin)
```

### Project CLAUDE.md 
Include "Key Decisions & Patterns":
```markdown
## Key Decisions & Patterns
- Token revocation at start of every request (for demo purposes)
- All fixes must be pipeline-integrated, not one-time
- OpenAPI spec bug: use `cat` not `jq -Rs .`
- Job IDs are integers, not strings
- Test collection has abstract auth provider
```

## 3. Session Logging

### Create session summary files:
```
user-guides/session-logs/2024-12-27-oneOf-jwt-fixes.md
```

Include:
- What was accomplished
- Key code changes
- Decisions made
- Next steps

### Quick session recap format:
```markdown
# Session: 2024-12-27
## Done:
- Fixed oneOf handling in pipeline
- Added token revocation to JWT script
- Started use case collection enhancement

## Key Points:
- Job IDs should be integers
- JWT shows "cannot revoke" error when no token (normal)
- Don't invent endpoints (GET /jobs/{id} doesn't exist)

## Next:
- Complete oneOf examples in use case collection
- Test in Postman
```

## 4. Correction Patterns That Work

### When I forget something:
❌ "You forgot about X"
✅ "Remember last week when we implemented X? It does Y"

### When I'm redoing work:
❌ "We already did this"
✅ "We already solved this by [specific solution] - it's in [specific file]"

### When I miss context:
❌ "You should know this"
✅ "This connects to our work on [specific feature] where we decided [specific approach]"

## 5. Key Phrases That Trigger Memory

Use these phrases to help me connect to past work:
- "Part of our pipeline work"
- "Like we did with [previous similar task]"
- "Following our pattern of..."
- "Using our standard approach..."
- "Remember our [specific decision] about..."

## 6. File References

Always mention the key files when relevant:
- "Check our jwt-pre-request.js for the revocation logic"
- "This goes in the Makefile pipeline section"
- "Update PROJECT_MEMORY.md with this"
- "Our CLAUDE.md says we do X"

## 7. Workflow Reminders

Before starting work:
1. "Let's check where we left off"
2. "Our standard workflow is..."
3. "Remember to update [specific file] after changes"

## 8. Pattern Recognition Helpers

When you see me starting to repeat mistakes:
- "Stop - we learned last time that..."
- "Check CLAUDE.md first - we documented this"
- "This is the [Nth] time - let's add it to our patterns"

## 9. Testing/Verification Reminders

- "Run our standard test: `make postman-instance-build-and-test`"
- "Check if this breaks our pipeline"
- "Verify this works with our existing [feature]"

## 10. What Helps Claude Most

1. **Explicit connections**: "This relates to our JWT work where we..."
2. **File locations**: "The working version is in..."
3. **Decision history**: "We chose X because Y"
4. **Pattern identification**: "We always do X when Y"
5. **Correction with context**: "Actually, we do X because [reason]"

## Example Session Start

```
"Hi Claude, continuing our C2M API work. 
Quick context:
- JWT script revokes tokens at start (shows full flow)
- oneOf fixes are pipeline-integrated
- We're adding all variants to use case collection
- Job IDs are integers
- Check CLAUDE.md for our patterns
Let's finish the use case collection enhancement."
```

## Quick Checklist for Complex Tasks

Before asking Claude to implement something:
- [ ] Mention if we've done similar before
- [ ] Reference the relevant files
- [ ] Note any decisions/patterns to follow
- [ ] Specify if it needs pipeline integration
- [ ] Remind about testing commands

## Memory Triggers

If you notice Claude forgetting, try:
1. "What does CLAUDE.md say about this?"
2. "How did we handle this last time?"
3. "Check our patterns in [file]"
4. "This should follow our pipeline approach"

---

Remember: The more specific the context, the better Claude can connect to previous work. Session summaries and updated CLAUDE.md files are the most powerful tools for maintaining continuity.