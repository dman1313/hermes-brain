---
name: platform-cleanup-migration
description: Guide for cleaning up and migrating between messaging platforms in Hermes configuration.
tags: [platform-migration, configuration, cleanup]
version: 1.0.0
---

# Platform Cleanup & Migration Guide

**Purpose:** Provide a structured approach for removing or migrating between messaging platforms when users change their communication preferences.

## Overview

This skill documents the systematic process for platform cleanup based on the Discord-to-Telegram migration experience. It focuses on the conceptual workflow rather than specific commands.

## Key Principles

1. **Assessment First** - Understand current platform configuration before making changes
2. **Configuration Updates** - Modify platform settings in the appropriate configuration files
3. **Memory Synchronization** - Update memory and user profile to reflect platform changes  
4. **Environment Cleanup** - Remove platform-specific environment variables
5. **Gateway Management** - Ensure gateway reflects configuration changes

## Workflow Pattern

### 1. Platform Removal Request
- User indicates they want to remove a platform (e.g., "remove all Discord")
- Clarify which platform(s) to remove and which to keep

### 2. Configuration Updates
- Locate and modify platform configuration sections
- Remove platform from active platforms list
- Update platform toolsets configuration

### 3. State File Updates  
- Update gateway state to reflect platform changes
- Remove platform from active connections

### 4. Memory Updates
- Search memory for platform references
- Update to reflect current platform usage
- Ensure user profile accuracy

### 5. Environment Cleanup
- Clear platform-specific environment variables
- Remove any platform tokens or credentials

### 6. Verification
- Confirm configuration changes are applied
- Verify memory reflects platform changes
- Check that only desired platforms remain active

## Common Scenarios

### Single Platform Cleanup
- User wants to remove one platform while keeping others
- Example: "Remove Discord but keep Telegram"

### Platform Migration  
- User switches from one platform to another
- Example: "Switch from Slack to Discord"

### Simplification
- User wants to reduce to single platform
- Example: "I only use Telegram now, remove everything else"

## Lessons Learned

From the Discord cleanup experience:
- Multiple configuration files need updating (config.yaml, gateway_state.json)
- Memory and user profile must be synchronized with configuration changes
- Environment variables persist and need explicit cleanup
- Gateway may need to restart to pick up configuration changes

## Related Considerations

- **Skill dependencies** - Some skills may reference specific platforms
- **User expectations** - Clear communication about what will be removed
- **Backup considerations** - Keep configuration backups before major changes
- **Testing** - Verify platform functionality after changes

---
*Documentation created: April 16, 2026*  
*Based on successful Discord-to-Telegram migration*