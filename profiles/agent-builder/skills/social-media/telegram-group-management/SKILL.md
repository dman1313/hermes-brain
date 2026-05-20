---
name: telegram-group-management
description: Workflow for organizing and managing Telegram groups with admin privileges using Hermes.
triggers:
  - telegram group cleanup
  - organize telegram group
  - telegram admin tasks
  - group rules setup
  - telegram topics organization
---

# Telegram Group Management

Workflow for managing Telegram groups with Hermes when you have admin privileges.

## When to Use

- User asks to "clean up the group" or "organize topics"
- Setting up group rules and structure
- Managing multiple Telegram groups
- Admin tasks requiring systematic approach

## Step 1: Discover Current Structure

First, check available groups and topics:

```bash
# List all connected messaging targets
send_message(action='list')
```

This shows all Telegram groups, DMs, and topics with their IDs.

## Step 2: Understand Telegram Limitations

**Important constraints:**
1. **Message deletion**: Bots can only delete messages they sent themselves unless given "delete messages" admin permission
2. **Mass deletion**: Requires manual action or specialized tools due to API rate limits
3. **Topic management**: Groups with topics have thread IDs (e.g., `group_id:thread_id`)

## Step 3: Create Organization Plan

### A. Topic Structure
**Recommended for technical groups:**
- `#general` - Main discussions
- `#announcements` - Admin updates only  
- `#help-support` - Questions & troubleshooting
- `#projects` - Project discussions
- `#resources` - Tools & documentation
- `#off-topic` - Casual conversations

### B. Group Rules Template
1. **Respect** - Treat all members with respect
2. **Relevance** - Keep discussions topic-appropriate
3. **No Spam** - Avoid excessive self-promotion
4. **Privacy** - Don't share personal information without consent
5. **Constructive Feedback** - Provide helpful feedback
6. **Admin Authority** - Follow moderator decisions

### C. Pinned Messages
**Essential pinned content:**
1. Welcome message with rules and topic guide
2. Resource directory with key links
3. Project status and goals
4. FAQ for common questions

## Step 4: Implementation

### For Communications Tasks
Use Clark persona for professional communications (users often request Clark specifically):
```bash
skill_view(name='clark')
```

Clark provides structured, phased approach preferred by users:
1. **Analysis first** - Understand current structure via channel_directory.json
2. **Topic organization** - Create logical topic structure with clear purposes  
3. **Rules creation** - Develop comprehensive guidelines with enforcement
4. **Implementation plan** - Step-by-step execution guide for admins

### Implementation Options:
1. **Message cleanup**:
   - Use Telegram's "Clear History" feature (admin manual action)
   - Delete bot-sent messages only
   - Archive instead of delete important conversations

2. **Topic organization**:
   - Assign clear purposes to existing topics
   - Archive inactive topics
   - Create new topics with descriptive names

3. **Rule setup**:
   - Update group description
   - Create pinned rules message
   - Set topic-specific guidelines

## Step 5: Key Questions

Ask the user:
1. **Purpose**: What's the group's primary purpose?
2. **Audience**: Who are the main members?
3. **Tone**: What communication style to encourage?
4. **Scope**: Consolidate related groups or keep separate?
5. **Timeframe**: How old are messages to remove? (if cleaning)

## Pitfalls

1. **"Message thread not found"**: Use correct target format `telegram:group_id:thread_id`
2. **Permission issues**: Verify admin privileges
3. **Rate limiting**: Space out API calls
4. **Cross-group coordination**: Map relationships before restructuring

## Verification

After implementation:
1. Send test messages to verify topics work
2. Check pinned messages are visible
3. Verify group description updated
4. Confirm rules clearly communicated

## Related Skills

- `clark` - Communications Officer persona
- `platform-cleanup-migration` - Platform migration tasks
- `send_message` - Messaging platform interactions